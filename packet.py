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
        # Length in bytes
        self.updatelen()

    # Update length field (in bytes)
    def updatelen(self):
        self.length = self.offsets["DATA"] + self.sizes["DATA"]
        self.setsegment("LENGTH", self.sizes["LENGTH"], self.length)

    # Add flag and add to header
    def addflag(self, flagname):
        flags = self.getsegment("FLAGS")
        flagbit = self.flagnames.get(flagname)
        flagsbit = int.from_bytes(flags, "big", signed=True)
        if flagbit is not None:
            #self.flags = (flagsbit | flagbit).to_bytes(1, "big")
            #self.setflag(self.flags)
            self.setsegment("FLAGS", self.sizes["FLAGS"], (flagsbit | flagbit).to_bytes(self.sizes["FLAGS"], "big"))

    # Delete flag and remove from header
    def delflag(self, flagname):
        flags = self.getsegment("FLAGS")
        flagbit = self.flagnames[flagname]
        flagsbit = int.from_bytes(flags, "big", signed=True)
        if flagbit is not None:
            if flagbit & flagsbit == flagbit:
                #self.flags = (flagsbit ^ flagbit).to_bytes(1, "big")
                #self.setflag(self.flags)
                self.setsegment("FLAGS", self.sizes["FLAGS"], (flagsbit ^ flagbit).to_bytes(self.sizes["FLAGS"], "big"))

    def getflag(self, flagname):
        flags = self.getsegment("FLAGS")
        flagbit = self.flagnames[flagname]
        flagsbit = int.from_bytes(flags, "big", signed=True)
        if flagbit is not None:
            return flagbit & flagsbit == flagbit


    # Set segment of the header based on offset and size. Size (bytes) is a required field for data segment.
    def setsegment(self, segname, size, data):
        if segname is not None:
            # Offset of the segment being updated
            offset = self.offsets.get(segname)

            # If DATA, change DATA size to match new payload
            if segname == "DATA":
                self.sizes["DATA"] = size

            if offset is not None and size is not None:
                # Byte data to be inserted
                bdata = bytearray(size)

                # Support for ints or byte arrays
                if isinstance(data, int):
                    bdata = data.to_bytes(size, "big")
                else:
                    bdata = data

                # New header byte array, update len to fit new data size
                if segname == "DATA":
                    self.updatelen()
                newheader = bytearray(self.length)

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

    def fromstring(self, data):
        # Copy entire buffer to packet temporarily
        self.header = data
        # Get the length of the actual buffer
        length = int.from_bytes(self.getsegment("LENGTH"), 'big', signed=True)
        # Get the length of the data field
        datalen = length - self.offsets["DATA"]

        # Set the header to the proper length
        self.header = data
        # Set the data size to the proper length
        self.sizes["DATA"] = datalen
        # Update the length field to match the new packet size
        self.updatelen()
        # Fix the internal flag value
        #self.flags = self.getsegment("FLAGS")

    def __len__(self):
        length = int.from_bytes(self.getsegment("LENGTH"), "big", signed=True)





