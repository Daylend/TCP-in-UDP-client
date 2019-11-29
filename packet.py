#!/usr/bin/python3


# Handles low level byte manipulation
class Packet:

    def __init__(self):

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

        self.header = bytearray(self.offsets["DATA"] + self.sizes["DATA"])
        self.flags = bytes(1)

    # Add flag and add to header
    def addflag(self, flagname):
        flagbit = self.flagnames.get(flagname)
        if flagbit is not None:
            self.flags = self.flags | flagbit
            self.setflag(self.flags)

    # Delete flag and remove from header
    def delflag(self, flagname):
        flagbit = self.flagnames.get(flagname)
        if flagbit is not None:
            if flagbit & self.flags == 1:
                self.flags = self.flags ^ flagbit
                self.setflag(self.flags)

    # Sets the FLAGS segment in the header
    def setflag(self, byte):
        self.setsegment("FLAGS", 1, self.flags)

    # Set segment of the header based on offset and size. Size (bytes) is a required field for data segment.
    def setsegment(self, segname, size, data):
        if segname is not None:
            offset = self.offsets.get(segname)

            if segname == "DATA":
                self.sizes["DATA"] = size

            if offset is not None and size is not None:
                # Byte data to be inserted
                bdata = bytearray(size)
                bdata = data.to_bytes(size, "big")

                # New header byte array
                newheaderlen = self.offsets["DATA"] + self.sizes["DATA"]
                newheader = bytearray(newheaderlen)

                for i in range(len(self.header)):
                    newheader[i] = self.header[i]

                for i in range(size):
                    newheader[offset + i] = bdata[i]

                self.header = newheader

    # Get segment of the header from segment name (bytearray)
    def getsegment(self, segname):
        if segname is not None:
            offset = self.offsets.get(segname)
            size = self.sizes.get(segname)

            if offset is not None and size is not None:
                return self.header[offset:offset+size]

