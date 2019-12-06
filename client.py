#!/usr/bin/python3

import packet
import Session

sess = Session.Session("127.0.0.1", 12001, 12000)
sess.connect()
filehandler = open('test.txt', 'wb')
filehandler.write(bytes(sess.databuffer))
filehandler.close()