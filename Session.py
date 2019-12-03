#!/usr/bin/python3

import packet
import socket
from collections import deque

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
        self.__window = deque()
        self.__lastack = 0
        self.__socket = self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__buffsize = 4096
        # Do I really need this?
        self.__established = False

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
                        self.__lastack = datapkt.getsegment("ACK")
                        # Alright send the ack ack ack ack ack
                        ackpacket = packet.Packet()
                        ackpacket.addflag("ACK")
                        # New SEQ is old ACK + new SEQ len
                        acklen = seqlen + ackpacket.length
                        ackpacket.setsegment("SEQ", seqpacket.sizes["SEQ"], acklen)
                        self.__socket.sendto(datapkt.header)
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
                        # Look at the stuff in the queue before we receive new data

                        # Make sure to handle FIN here as well
                        pass

                    # Okay now we can handle new data
                    data, address = self.__socket.recvfrom(self.__buffsize)
                    if data is not None:
                        datapkt = packet.Packet()
                        datapkt.fromstring(data)

                        # If this is the packet we're expecting to receive
                        if self.__islatestpacket(datapkt):
                            # If the incoming data is not finished
                            if not datapkt.getflag("FIN"):
                                # Get the data from the packet and send back an ack
                                pass

                            else:
                                isfin = True
                        else:
                            # Else throw it in the queue to look at later
                            self.__window.append(datapkt)
                    if isfin:
                        # Wrap up we're done here
                        pass
            except:
                pass

    # Check to make sure this is the next SEQ # we're expecting (last == current - len)
    def __islatestpacket(self, pkt):
        pass

    # Send ack for each data seq packet
    def __data_ack(self, seq):

        ackpkt = packet.Packet()
        ackpkt.addflag("ACK")
        ackpkt.setsegment("ACK", ackpkt.sizes["ACK"], seq)
        self.__lastack = seq
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




