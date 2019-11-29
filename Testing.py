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


if __name__ == '__main__':
    unittest.main()
