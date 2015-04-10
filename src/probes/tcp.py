import socket
import select
from probes import probe
import time

import logging
import logger_utils

logger = logging.getLogger("TCP")
logger.addFilter(logger_utils.Unique())


class TCPClient(probe.ProbeClient):
    def reconnect(self):
        logger.info("Reconnecting to %s:%s" % (self.address, self.port))
        self.connection = None
        self.connect()

    def test(self):
        msg = "Ping"
        self.connect()
        if self.connection:

            # TODO: Clear receive buffer first?

            send_time = time.time()

            try:
                l = self.connection.send(msg.encode("utf-8"))
                if l != len(msg):
                    logger.error("Cannot send ping message to %s:%s" % (self.address, self.port))
                    self.reconnect()
                    return
            except (socket.gaierror, OSError):
                logger.exception("Exception occurred when trying to send ping message!")
                self.reconnect()
                return

            # Ok message send, let's wait for response
            rx, wx, tx = select.select([self.connection], [], [], self.timeout)
            if len(rx) == 0:
                logger.error("Didn't receive reply from server in %s seconds" % self.timeout)
                return

            recv_time = time.time()

            try:
                response = self.connection.recv(1024)
            except (socket.gaierror, OSError):
                logger.exception("Cannot receive message!")
                self.reconnect()
                return

            if len(response) == 0:
                logger.error("Got zero size response, connection lost?")
                self.reconnect()
                return

            try:
                response = response.decode("utf-8")
            except UnicodeDecodeError:
                logger.exception("Got invalid or corrupted message '%s' from server!" % response)
                self.reconnect()
                return

            if response != "Pong":
                logger.error("Got invalid or corrupted response '%s' from server!" % response)
                self.reconnect()
                return

            logger.info("Got Pong message from server in %4.2f ms !" % ((recv_time - send_time) * 1000.0,))

    def connect(self):
        if self.connection is not None:
            return

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Wait for 5 x timeout (= 30) seconds before timeout
        self.connection.settimeout(self.timeout * 5)
        # Connect to server
        try:
            self.connection.connect((self.address, self.port))
        except (socket.gaierror, OSError):
            logger.exception("Cannot connect to server %s:%s" % (self.address, self.port))


class TCPServer(probe.ProbeServer):
    def _init_connection(self):
        if self.socket:
            return
        while not self.socket:
            logger.info("Trying to bind")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.bind((self.address, self.port))
            except (socket.gaierror, OSError):
                logger.error("Cannot bind to %s:%s" % (self.address, self.port))
                self.socket = None
                time.sleep(5)
                continue
            try:
                self.socket.listen(5)
            except (socket.gaierror, OSError):
                logger.error("Cannot listen on bind address")
                self.socket = None
                time.sleep(5)
                continue
        logger.info("Bind successfully, listening on %s:%s" % (self.address, self.port))

    def handle(self, msg, source):
        logger.info("Got message '%s' from %s" % (msg, source.source))
        try:
            l = source.conn.send("Pong".encode("utf-8"))
            if l == len("Pong"):
                return True
            else:
                logger.error("Length of send message too short, connection closed?")
                self.close_connection(source)
        except socket.gaierror:
            logger.exception("Cannot send response to %s" % (source.source,))
            self.close_connection(source)
            return
