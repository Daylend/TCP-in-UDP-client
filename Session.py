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
        self.__databuffer = ""

    def connect(self):
        self.__handshake()
        self.__data_recv()

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
            data, address = self.__socket.recvfrom(self.__buffsize)

            if data is not None:
                datapkt = packet.Packet()
                # Convert data string to packet
                datapkt.fromstring(data)

                # Confirm it's actually the packet we want
                if datapkt.getflag("ACK") and datapkt.getflag("SYN"):
                    # Make sure it's actually an ACK for our SYN
                    if datapkt.getsegment("ACK") == seqlen:
                        # Alright send the ack ack ack ack ack
                        ackpacket = packet.Packet()
                        ackpacket.addflag("ACK")
                        # New SEQ is old ACK + new SEQ len
                        acklen = seqlen + ackpacket.length
                        ackpacket.setsegment("SEQ", ackpacket.sizes["SEQ"], acklen)
                        # Ack = old SEQ
                        ackpacket.setsegment("ACK", ackpacket.sizes["ACK"], datapkt.getsegment("SEQ"))

                        self.__lastack = ackpacket.getsegment("ACK")

                        self.__socket.sendto(datapkt.header, self.address)
                        self.__established = True


        except:
            print("AHHHHHHHHHH")

    # Step 4, receive the data from server
    def __data_recv(self):
        if self.__established:
            try:
                isfin = False
                while not isfin:
                    if len(self.__window) > 0:
                        # Look at the stuff in the window before we receive new data
                        for pkt in self.__window:
                            if self.__islatestpacket(pkt):
                                # TODO: Pull the data from the data segment, send ack, update last ack
                                pass
                                if pkt.getflag("FIN"):
                                    isfin = True

                    # Okay now we can handle new data
                    data, address = self.__socket.recvfrom(self.__buffsize)
                    if data is not None:
                        datapkt = packet.Packet()
                        datapkt.fromstring(data)

                        # If this is the packet we're expecting to receive
                        if self.__islatestpacket(datapkt):
                            # If the incoming data is not finished
                            if not datapkt.getflag("FIN"):
                                # TODO: Get the data from the packet and send back an ack
                                pass

                            else:
                                isfin = True
                        else:
                            # Else throw it in the queue to look at later
                            dataseq = datapkt.getsegment("SEQ")
                            # Make sure the SEQ number is greater than the ACK we're expecting, otherwise it's a dupe
                            # TODO: Check for last ack and resend ACK if last ack
                            if dataseq > self.__lastack:
                                self.__window[datapkt] = dataseq
                    if isfin:
                        # TODO: Wrap up we're done here (fin was recvd)
                        pass
            except:
                print("AHHHHHHHHHHHHHHHHHHH")

    # Check to make sure this is the next SEQ # we're expecting (last == current - len)
    def __islatestpacket(self, pkt):
        # We have to make sure we're taking our ACK SEQ numbers into account. (45)
        seq = pkt.getsegment("SEQ")
        # If seq1 is 10, ack1 is 15, and seq2 is 23, we know latest packet is seq2 - seq2.length == lastack + ack.length
        return seq - pkt.length == self.__expectedseq()

    # We expect the next sequence number to be the last ACK + the last ACK's length + some unknown value greater than 45
    def __expectedseq(self):
        temp = packet.Packet()
        return self.__lastack + temp.length

    # Send ack for each received data seq packet
    def __data_ack(self, rseq):

        ackpkt = packet.Packet()
        ackpkt.addflag("ACK")
        ackpkt.setsegment("ACK", ackpkt.sizes["ACK"], rseq + ackpkt.length)
        self.__lastack = rseq
        pass

    # Step 6, receive fin from server
    def __connect_fin(self):
        pass

    # Step 7, send ack from fin to server
    def __connect_fin_ack(self):
        pass

    # Force disconnect from session
    def disconnect(self):
        pass




