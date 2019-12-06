#!/usr/bin/python3

import packet
import Session

sess = Session.Session("127.0.0.1", 10001)
sess.connect()