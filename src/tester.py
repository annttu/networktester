#!/usr/bin/env python
# encoding: utf-8
import argparse
import time
import database

from probes import tcp, udp, huawei
import location
import logging
import submitter


def maintcp(address, port):
    t = tcp.TCPClient(address, port)
    while True:
        time.sleep(1)
        t.test()


def mainudp(address, port):
    t = udp.UDPClient(address, port)
    while True:
        time.sleep(1)
        t.test()


def mainhuawei(address):
    t = huawei.HuaweiClient(address, None)
    while True:
        time.sleep(5)
        t.test()

def mainstats():
    t = submitter.Submitter()
    t.start()
    while t.is_alive():
        time.sleep(5)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("-s", '--server', help="Server address", default="0.0.0.0")
    p.add_argument('-p', '--port', help="Server port", default=5555, type=int)
    p.add_argument('-l', '--logfile', help="logfile", default=None)
    p.add_argument('-t', '--type', help="Type", default="tcp", choices=['tcp', 'udp', 'huawei', 'statistics'])
    p.add_argument('-d', '--debug', help="Debug", default=False, action="store_true")

    args = p.parse_args()

    level = logging.INFO
    if args.debug:
        level = logging.DEBUG

    logging.basicConfig(level=level, filename=args.logfile, format='%(asctime)s %(levelname)s %(name)s: %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S')

    # Init engine

    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
    logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.WARN)
    database.DB.connect()
    database.DB.create_tables()

    # Start locator

    location.start()

    try:

        if args.type == 'tcp':
            maintcp(address=args.server, port=args.port)

        elif args.type == 'huawei':
            mainhuawei(address=args.server)

        elif args.type == 'udp':
            mainudp(address=args.server, port=args.port)

        else:
            mainstats()

    except:
        location.stop()
        raise