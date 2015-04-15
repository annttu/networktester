import socket
import select
from probes import probe
import time
import logging
import logger_utils
from probes.probe import ClientConnection

logger = logging.getLogger("UDP")
logger.addFilter(logger_utils.Unique())


class UDPClient(probe.ProbeClient):

    def connect(self):
        if self.connection is not None:
            return

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Wait for timeout seconds before timeout, UDP and socket timeouts are not very useful anyway.
        self.connection.settimeout(self.timeout)
        # Connect to server
        try:
            self.connection.connect((self.address, self.port))
        except (socket.gaierror, OSError):
            logger.exception("Cannot connect to server %s:%s" % (self.address, self.port))

    def get_responses(self):

        rx, wx, tx = select.select([self.connection], [], [], 0.1)

        if len(rx) == 0:
            return

        try:
            response = self.connection.recv(1024)
            recv_time = time.time()
        except (socket.gaierror, OSError):
            logger.exception("Cannot receive message!")
            return

        if len(response) == 0:
            logger.error("Got zero size response, connection lost?")
            return

        if b"\x00" not in response:
            logger.error("Termination character not in message!")
            return

        try:
            response = response.decode("utf-8")
        except UnicodeDecodeError:
            logger.exception("Got invalid or corrupted message '%s' from server!" % response)
            return


        responses = response.split("\x00")[:-1]

        for response in responses:
            try:
                send_time = float(response[:-1])
            except ValueError:
                logger.exception("Got invalid or corrupted message '%s' from server!" % response)
                return

            logger.info("Got Pong message from server in %.2f ms !" % ((recv_time - send_time) * 1000.0,))

        return responses

    def test(self):

        self.connect()
        if self.connection:

            # TODO: Clear receive buffer first?

            while True:
                if self.get_responses() is None:
                    break

            msg = "%s\x00" % time.time()
            msg = msg.encode("utf-8")

            try:
                l = self.connection.send(msg)
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

            while True:
                if self.get_responses() is None:
                    break

    def reconnect(self):
        logger.info("Reconnecting to %s:%s" % (self.address, self.port))
        self.connection = None
        self.connect()


class UDPServer(probe.ProbeServer):
    def _init_connection(self):
        if self.socket:
            return
        while not self.socket:
            logger.info("Trying to bind")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                self.socket.bind((self.address, self.port))
            except (socket.gaierror, OSError):
                logger.error("Cannot bind to %s:%s" % (self.address, self.port))
                self.socket = None
                time.sleep(5)
                continue
        logger.info("Bind successfully, listening on %s:%s" % (self.address, self.port))

    def handle(self, msg, source):
        try:
            tmp_msg = msg.decode("utf-8")
        except UnicodeDecodeError:
            logger.error("Got message '%s' with invalid encoding from %s!" % (msg, source.source))
            return
        if not tmp_msg.endswith('\x00'):
            logger.error("Got not null terminated message from %s!" % (source.source,))
            return
        logger.debug("Got message '%s' from %s" % (logger_utils.safe_encode(tmp_msg[:-1]), source.source))
        try:
            # Send message back
            l = source.conn.sendto(msg, (source.source, source.port))
            if l == len(msg):
                return True
            else:
                logger.error("Length of send message too short, connection closed?")
                self.close_connection(source)
        except socket.gaierror:
            logger.exception("Cannot send response to %s" % (source.source,))
            self.close_connection(source)
            return

    def mainloop(self):
        rlist, wlist, xlist = select.select([self.socket], [], [self.socket])
        for conn in rlist:
            try:
                msg, addr = conn.recvfrom(1024)
            except (socket.gaierror, OSError):
                logger.exception("Failed to receive message from %s" % (addr[0],))
                continue
            if len(msg) == 0:
                logger.error("Got zero length message from %s!" % (addr[0],))
                continue
            else:
                self.handle(msg, ClientConnection(self.socket, addr))

