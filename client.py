#!/usr/bin/python3

import packet

pkt = packet.Packet()

pkt.setsegment("SEQ", pkt.sizes["SEQ"], 0x01010101)
pkt.setsegment("ACK", pkt.sizes["ACK"], 0x02020202)
pkt.setsegment("LENGTH", pkt.sizes["LENGTH"], 45)
pkt.setsegment("DATA", 9, 0x010203040506070809)

print(pkt.getsegment("SEQ"))
print(pkt.getsegment("ACK"))
print(pkt.getsegment("LENGTH"))
print(pkt.getsegment("DATA"))

print("PACKET 2:")

pkt2 = packet.Packet()
pkt2.fromstring(b'\x00\xbcaN\x00\x00\x15\xb3\x00\x00\x00-\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
print(pkt2.getsegment("SEQ"))
print(pkt2.getsegment("ACK"))
print(pkt2.getsegment("LENGTH"))
print(pkt2.getsegment("DATA"))

print(int.from_bytes(pkt2.getsegment("SEQ"), "big", signed=True))
print(int.from_bytes(pkt2.getsegment("ACK"), "big", signed=True))
print(int.from_bytes(pkt2.getsegment("LENGTH"), "big", signed=True))
print(int.from_bytes(pkt2.getsegment("DATA"), "big", signed=True))
print(pkt2.getflag("SYN"))
pkt2.delflag("SYN")
print(pkt2.getflag("SYN"))
pkt2.addflag("SYN")
print(pkt2.getflag("SYN"))