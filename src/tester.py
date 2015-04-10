#!/usr/bin/env python
# encoding: utf-8
import argparse
import time

from probes import tcp
import logging


def main(address, port):
    t = tcp.TCPClient(address, port)
    while True:
        time.sleep(1)
        t.test()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("-s", '--server', help="Server address", default="0.0.0.0")
    p.add_argument('-p', '--port', help="Server port", default=5555, type=int)
    p.add_argument('-l', '--logfile', help="logfile", default=None)
    p.add_argument('-d', '--debug', help="Debug", default=False, action="store_true")

    args = p.parse_args()

    level = logging.INFO
    if args.debug:
        level = logging.DEBUG

    logging.basicConfig(level=level, filename=args.logfile, format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S')

    main(address=args.server, port=args.port)