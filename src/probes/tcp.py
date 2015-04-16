import socket
import select
from probes import probe
import database
import time
from location import locator
import logging
import logger_utils

logger = logging.getLogger("TCP")
logger.addFilter(logger_utils.Unique())


class TCPClient(probe.ProbeClient):
    def reconnect(self):
        logger.info("Reconnecting to %s:%s" % (self.address, self.port))
        self.save_status("RECONNECT", 0.0)
        self.connection = None
        self.connect()

    def save_status(self, status, value):
        l = locator.get_location()
        s = database.DB.get_session()
        t = database.TCPCoordTable()
        t.status = status
        t.value = value
        t.elevation = l.ele
        t.lat = l.lat
        t.lon = l.lon
        t.speed = l.speed
        s.add(t)
        s.commit()
        s.close()

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

            t = (recv_time - send_time) * 1000.0

            self.save_status("OK", t)

            logger.info("Got Pong message from server in %.2f ms !" % (t,))

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
        self.save_status("CONNECT", 0.0)

