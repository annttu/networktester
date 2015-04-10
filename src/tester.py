#!/usr/bin/env python
# encoding: utf-8
import time

from probes import tcp
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

def main():
    t = tcp.TCPClient("127.0.0.1", 5555)
    while True:
        time.sleep(1)
        t.test()


if __name__ == '__main__':
    main()