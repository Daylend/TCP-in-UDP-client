#!/usr/bin/python3

import packet
import Session
import time

done = False
while not done:
    sess = Session.Session("127.0.0.1", 12222, 11111)
    try:
        sess.connect()
        filehandler = open('test.zip', 'wb')
        filehandler.write(bytes(sess.databuffer))
        filehandler.close()
        done = True
    except Exception as e:
        print("EXCEPTION: " + str(e))
    finally:
        sess.disconnect()
        time.sleep(1)
