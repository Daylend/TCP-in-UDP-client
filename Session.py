#!/usr/bin/python3

import packet


# Implements the session logic using packets
class Session:

    def __init__(self, dest, port):
        self.destination = dest
        self.port = port
        self.states = {
            "CLIENT_CONNECT_SYN",
            "SERVER_CONNECT_SYN_ACK",
            "CLIENT_CONNECT_ACK",
            "SERVER_DATA_SEND",
            "CLIENT_DATA_ACK",
            "SERVER_FIN",
            "CLIENT_FIN_ACK"
        }
        self.window = {}

    def connect(self):
        pass

    def connect_syn(self):
        pass

    def connect_recv_syn_ack(self):
        pass

    def connect_ack(self):
        pass

    def data_recv(self):
        pass

    def data_ack(self):
        pass



