#!/usr/bin/env python
# encoding: utf-8


from probes import tcp
import logging
import logger_utils

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

logging.getLogger().addFilter(logger_utils.Unique())


def main():
    t = tcp.TCPServer("127.0.0.1", 5555)
    t.start()
    t.join()

if __name__ == '__main__':
    main()


