#!/usr/bin/python3

import packet

packet = packet.Packet("")

packet.setsegment("SEQ", 0x11111111)
packet.setsegment("ACK", 0x3e426001)
print(packet.header)