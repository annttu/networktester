import threading
import time
from gps import GPS, WATCH_ENABLE, client
import logging
from datetime import datetime, timedelta


logger = logging.getLogger("location")


class Location(object):
    def __init__(self):
        self.lat = None
        self.lon = None
        self.speed = None
        self.ele = None
        self.time = None

    def set(self, lat, lon, speed, ele):
        self.lat = lat
        self.lon = lon
        self.speed = speed
        self.ele = ele
        self.time = datetime.now()

    def check(self):
        if not self.time:
            return
        if self.time < (datetime.now() - timedelta(seconds=15)):
            self.lat = None
            self.lon = None
            self.speed = None
            self.ele = None

    def __str__(self):
        return "<%s, %s> speed: %s ele: %s" % (self.lat, self.lon, self.speed, self.ele)


class GPSPoller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.session = None
        self.current_value = Location()
        self._stopped = False
        self._skipped = 0

    def connect(self):
        if self.session:
            return
        try:
            self.session = GPS(mode=WATCH_ENABLE)
        except OSError:
            return

    def get_location(self):
        return self.current_value

    def stop(self):
        self._stopped = True

    def run(self):
        while not self._stopped:
            self.current_value.check()
            self.connect()
            if not self.session:
                time.sleep(1)
                continue
            try:
                v = self.session.next()
                if 'lat' in dict(v):
                    alt = None
                    if 'alt' in dict(v):
                        alt = v['alt']
                    self.current_value.set(v['lat'], v['lon'], v['speed'], alt)
                self._skipped = 0
            except StopIteration:
                self._skipped += 1
                if self._skipped > 20:
                    self.session = None
                time.sleep(0.5)
            except client:
                logger.exception("Client exception")
                time.sleep(0.5)
            except Exception:
                logger.exception("Unknown exception")
                time.sleep(0.5)


locator = GPSPoller()


def start():
    locator.start()


def stop():
    locator.stop()
    locator.join()


if __name__ == '__main__':

    locator.start()
    while 1:
        time.sleep(5)
        print("data")
        print(locator.get_location())