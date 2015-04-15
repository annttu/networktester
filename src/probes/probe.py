import select
import socket
import abc
import threading


import logging
import logger_utils

logger = logging.getLogger("Probe")
logger.addFilter(logger_utils.Unique())


class ClientConnection(object):
    def __init__(self, connection, source):
        self.conn = connection
        self.source = source[0]
        self.port = source[1]


class ProbeClient(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, address, port, timeout=5):
        self.address = address
        self.port = port
        self.connection = None
        self.timeout = timeout
        self.connect()

    @abc.abstractmethod
    def reconnect(self):
        pass

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def test(self):
        pass


class ProbeServer(threading.Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = None
        self.connections = []
        threading.Thread.__init__(self)
        self._init_connection()
        self._stop = False

    @abc.abstractmethod
    def _init_connection(self):
        pass

    @abc.abstractmethod
    def handle(self, msg, source):
        pass

    def close_connection(self, connection):
        logger.error("Closing connection to %s" % connection.source)
        try:
            connection.conn.close()
        except (socket.gaierror, OSError):
            logger.exception("Cannot close connection clearly")
        x = self.connections.index(connection)
        self.connections.pop(x)

    def stop(self):
        self._stop = True


    def run(self):
        self._init_connection()
        while not self._stop:
            self.mainloop()

    @abc.abstractmethod
    def mainloop(self):
        pass
