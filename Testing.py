#!/usr/bin/python3

import unittest
import packet
import Session


class TestPacketByteManip(unittest.TestCase):
    def test_setsegment(self):
        pckt = packet.Packet()

        seg1 = 0x01010101
        seg2 = 0x02020202
        seg3 = 0x03030303
        seg4 = 0x010203040506070809

        pckt.setsegment("SEQ", pckt.sizes["SEQ"], seg1)
        pckt.setsegment("ACK", pckt.sizes["ACK"], seg2)
        pckt.setsegment("LENGTH", pckt.sizes["LENGTH"], seg3)
        pckt.setsegment("DATA", 9, seg4)

        getSeg1 = pckt.getsegment("SEQ")
        getSeg2 = pckt.getsegment("ACK")
        getSeg3 = pckt.getsegment("LENGTH")
        getSeg4 = pckt.getsegment("DATA")

        self.assertEqual(seg1.to_bytes(4, "big"), getSeg1)
        self.assertEqual(seg2.to_bytes(4, "big"), getSeg2)
        self.assertEqual(seg3.to_bytes(4, "big"), getSeg3)
        self.assertEqual(seg4.to_bytes(9, "big"), getSeg4)

    def test_fromstring(self):
        pkt2 = packet.Packet()

        seg1 = 12345678
        seg2 = 5555
        seg3 = 45

        pkt2.fromstring(
            b'\x00\xbcaN\x00\x00\x15\xb3\x00\x00\x00-\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

        getSeg1 = pkt2.getsegment("SEQ")
        getSeg2 = pkt2.getsegment("ACK")
        getSeg3 = pkt2.getsegment("LENGTH")

        self.assertEqual(seg1.to_bytes(4, "big"), getSeg1)
        self.assertEqual(seg2.to_bytes(4, "big"), getSeg2)
        self.assertEqual(seg3.to_bytes(4, "big"), getSeg3)
        self.assertEqual(pkt2.getflag("SYN"), True)


if __name__ == '__main__':
    unittest.main()
