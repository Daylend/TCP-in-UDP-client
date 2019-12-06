#!/usr/bin/python3

import packet
import socket
from collections import OrderedDict

# Implements the session logic using packets
class Session:

    def __init__(self, dest, port):
        self.address = (dest, port)
        self.__states = {
            "CLIENT_CONNECT_SYN",
            "SERVER_CONNECT_SYN_ACK",
            "CLIENT_CONNECT_ACK",
            "SERVER_DATA_SEND",
            "CLIENT_DATA_ACK",
            "SERVER_FIN",
            "CLIENT_FIN_ACK"
        }
        # Ordered dict = sorted buffer window by SEQ number = no iterating through list/queue
        self.__window = OrderedDict()
        self.__lastack = 0
        self.__socket = self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__buffsize = 4096
        # Do I really need this?
        self.__established = False
        # Byte array or string? Does it matter really?
        self.databuffer = bytearray(0)

    def connect(self):
        # Reset all the information from potential previous sessions
        self.__init__(self.address[0], self.address[1])
        # Run 3 way handshake against client
        self.__handshake()
        # Receive data from server. This will terminate the connection automatically after data is received.
        self.__data_recv()

    def print_packet(self, pkt, recvd):
        seq = str(int.from_bytes(pkt.getsegment("SEQ"), "big", signed=True))
        ack = str(int.from_bytes(pkt.getsegment("ACK"), "big", signed=True))
        len = str(int.from_bytes(pkt.getsegment("LENGTH"), "big", signed=True))
        flags = str(pkt.getsegment("FLAGS"))
        data = str(pkt.getsegment("DATA"))

        if recvd:
            print("RECEIVED")
        else:
            print("SENT")
        print("Packet: " + str(pkt.header))
        print("SEQ: " + seq + " ACK: " + ack + " LEN: " + len + " FLAGS: " + flags)
        print("DATA: " + data)
        print("----------------")

    # Attempt to 3-way handshake. Will give up if anything goes wrong.
    def __handshake(self):
        # SEQ packet
        seqpacket = packet.Packet()
        seqpacket.addflag("SYN")
        # We'll use this later
        seqlen = seqpacket.length
        seqpacket.setsegment("SEQ", seqpacket.sizes["SEQ"], seqlen)

        try:
            self.__socket.sendto(seqpacket.header, self.address)
            self.print_packet(seqpacket, False)
            data, address = self.__socket.recvfrom(self.__buffsize)

            if data is not None:
                datapkt = packet.Packet()
                # Convert data string to packet
                datapkt.fromstring(data)
                self.print_packet(datapkt, True)

                # Confirm it's actually the packet we want
                if datapkt.getflag("ACK") and datapkt.getflag("SYN"):
                    # Make sure it's actually an ACK for our SYN
                    if int.from_bytes(datapkt.getsegment("ACK"), "big", signed=True) == seqlen:
                        # Alright send the ack ack ack ack ack
                        #ackpacket = packet.Packet()
                        #ackpacket.addflag("ACK")
                        # New SEQ is old ACK + new SEQ len
                        #acklen = seqlen + ackpacket.length
                        #ackpacket.setsegment("SEQ", ackpacket.sizes["SEQ"], acklen)
                        # Ack = old SEQ
                        #ackpacket.setsegment("ACK", ackpacket.sizes["ACK"], datapkt.getsegment("SEQ"))

                        #self.__lastack = ackpacket.getsegment("ACK")

                        #self.__socket.sendto(ackpacket.header, self.address)
                        self.__data_ack(datapkt.getsegment("SEQ"))
                        #self.print_packet(ackpacket)
                        self.__established = True

        except TimeoutError:
            print("AHHHHHHHHHH")

    # Receive the data from server
    def __data_recv(self):
        if self.__established:
            try:
                isfin = False
                while not isfin:
                    # Look at the stuff in the window before we receive new data
                    if len(self.__window) > 0:
                        for pkt in self.__window:
                            if self.__islatestpacket(pkt):

                                # Pull the data from the data segment, send ack, delete from window
                                self.__appendbuffer(pkt.getsegment("DATA"))
                                self.__data_ack(pkt.getsegment("SEQ"))

                                if pkt.getflag("FIN"):
                                    # If FIN, then gracefully disconnect
                                    isfin = True
                                    self.__fin_ack(pkt.getsegment("SEQ"))
                                    self.disconnect()

                                # Make sure to remove the packet from the window
                                del(self.__window[pkt])
                                # TODO: ?MAYBE? add edge case to remove packets under the current SEQ if found,
                                #  shouldnt happen though (low priority)
                                # Break out of checking packets in the window as we found the one we want
                                # This might be redundant but I don't want to think about it rn
                                break

                    # Okay now we can handle new data
                    data, address = self.__socket.recvfrom(self.__buffsize)
                    if data is not None:
                        datapkt = packet.Packet()
                        datapkt.fromstring(data)
                        self.print_packet(datapkt, True)

                        # If this is the packet we're expecting to receive
                        if self.__islatestpacket(datapkt):
                            # If the incoming data is not finished
                            if not datapkt.getflag("FIN"):
                                # Get the data from the packet and send back an ack
                                self.__appendbuffer(datapkt.getsegment("DATA"))
                                self.__data_ack(datapkt.getsegment("SEQ"))

                            else:
                                # If FIN, then gracefully disconnect
                                isfin = True
                                self.__fin_ack(datapkt.getsegment("SEQ"))
                                self.disconnect()
                        else:
                            # Else throw it in the queue to look at later
                            dataseq = datapkt.getsegment("SEQ")

                            # Make sure the SEQ number is greater than the ACK we last sent, otherwise it's a dupe
                            # TODO: Check for last ack and resend ACK if last ack (low priority)
                            if dataseq > self.__lastack:
                                self.__window[datapkt] = dataseq
            except TimeoutError:
                print("AHHHHHHHHHHHHHHHHHHH")

    # Check to make sure this is the next SEQ # we're expecting (last == current - len)
    def __islatestpacket(self, pkt):
        # We have to make sure we're taking our ACK SEQ numbers into account. (45)
        seq = int.from_bytes(pkt.getsegment("SEQ"), "big", signed=True)
        # If seq1 is 10, ack1 is 15, and seq2 is 23, we know latest packet is seq2 - seq2.length == lastack + ack.length
        return seq - pkt.length == self.__expectedseq()

    def __islastpacket(self, pkt):
        # TODO: Check to see if this is the same packet as the one that was last ack'd
        #   This requires us to remember 2 ACK values. (low priority)
        seq = pkt.getsegment("SEQ")

    # We expect the next sequence number to be the last ACK + the last ACK's length + some unknown value greater than 45
    def __expectedseq(self):
        temp = packet.Packet()
        return self.__lastack + temp.length

    def __appendbuffer(self, data):
        # Chances are this doesn't work but I'm lazy so let's find out
        self.databuffer += bytearray(data)

    # Send ack for each received data seq packet
    def __data_ack(self, rseq):
        # Should be a byte then so convert to int
        if not isinstance(rseq, int):
            rseq = int.from_bytes(rseq, "big", signed=True)
        ackpkt = packet.Packet()
        ackpkt.addflag("ACK")
        ackpkt.setsegment("SEQ", ackpkt.sizes["SEQ"], rseq + ackpkt.length)
        ackpkt.setsegment("ACK", ackpkt.sizes["ACK"], rseq)
        self.__lastack = rseq
        self.__socket.sendto(ackpkt.header, self.address)
        self.print_packet(ackpkt, False)

    # Send fin ack from fin to server
    def __fin_ack(self, rseq):
        finpkt = packet.Packet()
        finpkt.addflag("FIN")
        finpkt.addflag("ACK")
        finpkt.setsegment("SEQ", finpkt.sizes["SEQ"], rseq + finpkt.length)
        finpkt.setsegment("ACK", finpkt.sizes["ACK"], rseq)
        self.__lastack = rseq
        self.__socket.sendto(finpkt.header, self.address)
        self.print_packet(finpkt, False)

    # Disconnect from session. This can be after a graceful release or forced.
    def disconnect(self):
        self.__socket.close()
        self.__established = False



