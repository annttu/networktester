#!/usr/bin/env python
# encoding: utf-8


from probes import tcp
import logging
import logger_utils
import argparse


logging.getLogger().addFilter(logger_utils.Unique())


def main(address, port):
    t = tcp.TCPServer(address, port)
    t.start()
    t.join()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("-a", '--address', help="Server address", default="0.0.0.0")
    p.add_argument('-p', '--port', help="Server port", default=5555, type=int)
    p.add_argument('-l', '--logfile', help="logfile", default=None)
    p.add_argument('-d', '--debug', help="Debug", default=False, action="store_true")

    args = p.parse_args()

    level = logging.INFO
    if args.debug:
        level = logging.DEBUG

    logging.basicConfig(level=level, filename=args.logfile, format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S')

    main(address=args.address, port=args.port)


