import json
import socket
import select
import configuration
import database
from probes import probe
import time
import logging
import logger_utils
import location
import threading
import requests


logger = logging.getLogger("Submitter")

headers = {
    'User-Agent': 'Network tester version %s' % configuration.version,
    'Content-type': 'application/json'
}

KEYS = ['lat', 'lon', 'speed', 'elevation', 'value', 'timestamp', 'status']

class Submitter(threading.Thread):
    def __init__(self):
        self.connection = None
        threading.Thread.__init__(self)
        self._stopped = False
        self.s = requests.Session()
        self.s.headers.update(headers)
        self.verify = configuration.submit_verify_ssl
        self.submit_url = "%s/api/import/?key=%s" % (configuration.submit_url.rstrip("/"), configuration.submit_key)

    def stop(self):
        self._stopped = True

    def mainloop(self):
        s = database.DB.get_session()
        data = {
            'tcp': [],
            'udp': []
        }
        to_send = 0
        tcp_rows = s.query(database.TCPCoordTable).filter(database.TCPCoordTable.reported==False).limit(1000).all()
        to_send += len(tcp_rows)
        for i in tcp_rows:
            item = {k: v for k, v in vars(i).items() if k in KEYS}
            item['timestamp'] = item['timestamp'].isoformat()
            data['tcp'].append(item)
        udp_rows = s.query(database.UDPCoordTable).filter(database.UDPCoordTable.reported==False).limit(1000).all()
        to_send += len(udp_rows)
        for i in udp_rows:
            item = {k: v for k, v in vars(i).items() if k in KEYS}
            item['timestamp'] = item['timestamp'].isoformat()
            data['udp'].append(item)

        if to_send < 200:
            # send only if enough
            return
        # send data to server
        response = self.s.post(self.submit_url, data=json.dumps(data), verify=self.verify)
        if response.status_code == 200:
            for i in tcp_rows:
                i.reported=True
                s.add(i)
            for i in udp_rows:
                i.reported=True
                s.add(i)
            s.commit()
            logger.info("Successfully submitted data")
        else:
            logger.error("Got result %s from stats server with url %s" % (response.status_code, self.submit_url))

    def run(self):
        while not self._stopped:
            try:
                self.mainloop()
            except Exception:
                logger.exception("Unhandled exception occurred")
            time.sleep(5)