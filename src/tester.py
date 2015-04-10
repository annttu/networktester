#!/usr/bin/env python
# encoding: utf-8
import argparse
import time

from probes import tcp
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

def main(address, port):
    t = tcp.TCPClient(address, port)
    while True:
        time.sleep(1)
        t.test()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("-s", '--server', help="Server address", default="0.0.0.0")
    p.add_argument('-p', '--port', help="Server port", default=5555, type=int)

    args = p.parse_args()

    main(address=args.server, port=args.port)