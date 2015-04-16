import socket
import select
from probes import probe
import time
import logging
import logger_utils

logger = logging.getLogger("Server")
logger.addFilter(logger_utils.Unique())


class TCPServer(probe.ProbeServer):
    def _init_connection(self):
        if self.socket:
            return
        while not self.socket:
            logger.info("TCP: Trying to bind")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.bind((self.address, self.port))
            except (socket.gaierror, OSError):
                logger.error("TCP: Cannot bind to %s:%s" % (self.address, self.port))
                self.socket = None
                time.sleep(5)
                continue
            try:
                self.socket.listen(5)
            except (socket.gaierror, OSError):
                logger.error("TCP: Cannot listen on bind address")
                self.socket = None
                time.sleep(5)
                continue
        logger.info("TCP: Bind successfully, listening on %s:%s" % (self.address, self.port))

    def handle(self, msg, source):
        try:
            tmp_msg = msg.decode("utf-8")
        except UnicodeDecodeError:
            logger.error("TCP: Got message '%s' with invalid encoding from %s!" % (msg, source.source))
            return
        if not tmp_msg.endswith('\x00'):
            logger.error("TCP: Got not null terminated message from %s!" % (source.source,))
            return
        logger.debug("TCP: Got message '%s' from %s" % (logger_utils.safe_encode(tmp_msg[:-1]), source.source))
        try:
            # Send message back
            l = source.conn.send(msg)
            if l == len(msg):
                return True
            else:
                logger.error("TCP: Length of send message too short, connection closed?")
                self.close_connection(source)
        except socket.gaierror:
            logger.exception("TCP: Cannot send response to %s" % (source.source,))
            self.close_connection(source)
            return

    def mainloop(self):
        x = [x.conn for x in self.connections] + [self.socket]
        rlist, wlist, xlist = select.select(x, [], x)
        for conn in rlist:
            if conn == self.socket:
                conn, address = self.socket.accept()
                c = probe.ClientConnection(conn, address)
                self.connections.append(c)
            else:
                # Find connection
                connection = None
                for x in self.connections:
                    if conn == x.conn:
                        connection = x
                        break

                if not connection:
                    logger.error("TCP: BUG: Cannot find connection from connections!")
                    continue
                try:
                    msg = conn.recv(1024)
                except (socket.gaierror, OSError, socket.error):
                    logger.exception("TCP: Failed to receive message from %s" % (connection.source,))
                    self.close_connection(connection)
                    continue
                if len(msg) == 0:
                    logger.error("TCP: Got zero length message from %s!" % (connection.source,))
                    self.close_connection(connection)
                    continue
                else:
                    self.handle(msg, connection)

        for conn in xlist:
            if  conn == self.socket:
                logger.error("TCP: Exception occurred in socket, reconnecting")
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
                    logger.error("TCP: BUG: Cannot find connection from connections!")
                    continue
                self.close_connection(connection)


class UDPServer(probe.ProbeServer):
    def _init_connection(self):
        if self.socket:
            return
        while not self.socket:
            logger.info("UDP: Trying to bind")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                self.socket.bind((self.address, self.port))
            except (socket.gaierror, OSError):
                logger.error("UDP: Cannot bind to %s:%s" % (self.address, self.port))
                self.socket = None
                time.sleep(5)
                continue
        logger.info("UDP: Bind successfully, listening on %s:%s" % (self.address, self.port))

    def handle(self, msg, source):
        try:
            tmp_msg = msg.decode("utf-8")
        except UnicodeDecodeError:
            logger.error("UDP: Got message '%s' with invalid encoding from %s!" % (msg, source.source))
            return
        if not tmp_msg.endswith('\x00'):
            logger.error("UDP: Got not null terminated message from %s!" % (source.source,))
            return
        logger.debug("UDP: Got message '%s' from %s" % (logger_utils.safe_encode(tmp_msg[:-1]), source.source))
        try:
            # Send message back
            l = source.conn.sendto(msg, (source.source, source.port))
            if l == len(msg):
                return True
            else:
                logger.error("UDP: Length of send message too short, connection closed?")
                self.close_connection(source)
        except socket.gaierror:
            logger.exception("UDP: Cannot send response to %s" % (source.source,))
            self.close_connection(source)
            return

    def mainloop(self):
        rlist, wlist, xlist = select.select([self.socket], [], [self.socket])
        for conn in rlist:
            try:
                msg, addr = conn.recvfrom(1024)
            except (socket.gaierror, OSError, socket.error):
                logger.exception("UDP: Failed to receive message from %s" % (addr[0],))
                continue
            if len(msg) == 0:
                logger.error("UDP: Got zero length message from %s!" % (addr[0],))
                continue
            else:
                self.handle(msg, probe.ClientConnection(self.socket, addr))

