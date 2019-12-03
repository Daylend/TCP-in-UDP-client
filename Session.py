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
        self.__socket = self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__buffsize = 4096
        # Do I really need this?
        self.__established = False

    def connect(self):
        pass

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
                        ackpacket.setsegment("SEQ", seqpacket.sizes["SEQ"], acklen)
                        self.__socket.sendto(datapkt.header)
                        self.__established = True


        except:
            print("AHHHHHHHHHH")


    # Step 4, receive the data from server
    def __data_recv(self):
        pass

    # Step 5, send ack for each data packet from server
    def __data_ack(self):
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




