#!/usr/bin/python3


class Packet:

    def __init__(self, dest):
        self.dest = dest
        self.header = bytearray(47)
        self.flags = bytes(1)

        # Offset of each header segment
        self.offsets = {
            "SEQ": 0,
            "ACK": 4,
            "LENGTH": 8,
            "FLAGS": 12,
            "SHA": 13,
            "DATA": 45
        }

        # Length of each header segment
        self.sizes = {
            "SEQ": 4,
            "ACK": 4,
            "LENGTH": 4,
            "FLAGS": 1,
            "SHA": 32,
            "DATA": 0   # default 0 with no data
        }

        # Least significant to most significant bit
        self.flagnames = {
            "FIN": 0x01,
            "SYN": 0x02,
            "ACK": 0x04,
            "RST": 0x08
        }

    def addflag(self, flagname):
        flagbit = self.flagnames.get(flagname)
        if flagbit is not None:
            self.flags = self.flags | flagbit

    def delflag(self, flagname):
        flagbit = self.flagnames.get(flagname)
        if flagbit is not None:
            if flagbit & self.flags == 1:
                self.flags = self.flags ^ flagbit