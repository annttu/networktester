import socket
import select
from probes import probe
import database
import time
from location import locator
import logging
import logger_utils
from probes.probe import ClientConnection

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
            l = source.conn.send(msg)
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
        x = [x.conn for x in self.connections] + [self.socket]
        rlist, wlist, xlist = select.select(x, [], x)
        for conn in rlist:
            if conn == self.socket:
                conn, address = self.socket.accept()
                c = ClientConnection(conn, address)
                self.connections.append(c)
            else:
                # Find connection
                connection = None
                for x in self.connections:
                    if conn == x.conn:
                        connection = x
                        break

                if not connection:
                    logger.error("BUG: Cannot find connection from connections!")
                    continue
                try:
                    msg = conn.recv(1024)
                except (socket.gaierror, OSError, socket.error):
                    logger.exception("Failed to receive message from %s" % (connection.source,))
                    self.close_connection(connection)
                    continue
                if len(msg) == 0:
                    logger.error("Got zero length message from %s!" % (connection.source,))
                    self.close_connection(connection)
                    continue
                else:
                    self.handle(msg, connection)

        for conn in xlist:
            if  conn == self.socket:
                logger.error("Exception occurred in socket, reconnecting")
                for connection in self.connections:
                    self.close_connection(connection)
                self.socket = None
                self._init_connection()
            else:
                for x in self.connections:
                    if conn == x.conn:
                        connection = x
                        break

                if not connection:
                    logger.error("BUG: Cannot find connection from connections!")
                    continue
                self.close_connection(connection)