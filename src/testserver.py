#!/usr/bin/env python
# encoding: utf-8


from probes import tcp
import logging
import logger_utils
import argparse

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

logging.getLogger().addFilter(logger_utils.Unique())


def main(address, port):
    t = tcp.TCPServer(address, port)
    t.start()
    t.join()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("-a", '--address', help="Server address", default="0.0.0.0")
    p.add_argument('-p', '--port', help="Server port", default=5555, type=int)

    args = p.parse_args()

    main(address=args.address, port=args.port)


