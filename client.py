#!/usr/bin/python3

import packet

packet = packet.Packet()

packet.setsegment("SEQ", packet.sizes["SEQ"], 0x01010101)
packet.setsegment("ACK", packet.sizes["ACK"], 0x02020202)
packet.setsegment("LENGTH", packet.sizes["LENGTH"], 0x03030303)
packet.setsegment("DATA", 9, 0x010203040506070809)

print(packet.getsegment("SEQ"))
print(packet.getsegment("ACK"))
print(packet.getsegment("LENGTH"))
print(packet.getsegment("DATA"))