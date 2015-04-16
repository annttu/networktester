import database
import location
import random
from probes import probe
import requests
import requests.exceptions
import xml.etree.ElementTree as ET
import logging


logger = logging.getLogger("Huawei")

signals = {
    '0': '18',
    '1': '19',
    '2': '20',
    '3': '21',
    '4': '22',
    '5': '23',
}

sim = {

}

statuses = {
    'WIFI_ON': '2',
    'WIFI_TRANS': '3',
    'WIFI_OFF': '4',
    'NO_SIM': '14',
    'SIM_NORMAL': '15',
    'SIM_PIN_LOCKED': '16',
    'SIM_ERROR': '17',
    'SIM_PUK_LOCKED': '54',
    'NO_CONNECT': '24',
    'CONNECTING': '25',
    'CONNECTED': '26',
    'MODE_OFF': '27',
    'MODE_2G': '28',
    'MODE_3G': '29',
    'MODE_4G': '30',
    'ROAM_HOME': '31',
    'ROAM_ROAMING': '32',
    'ROAM_FORBID': '33',
    'SMS_EMPTY': '48',
    'SMS_NEW': '49',
    'SMS_FULL': '50',
    'SMS_READED': '58',
    'SIMLOCK_LOCKED': '56',
    'NO_SERVICE': '57',
    'MODE_SIM_DISABLE': '59',
    'MODE_2G_TRANS': '60',
    'MODE_3G_TRANS': '61',
    'MODE_4G_TRANS': '62',
    'WAN_ERR_CODE': '0'
}


def get_signal(address):
    r = requests.post(address)

    if r.status_code != 200:
        return None

    out = {}
    root = ET.fromstring(r.content.decode("utf-8"))
    for child in root:
        if child.tag == "SIG":
            for k,v in signals.items():
                if v == child.text:
                    out["signal"] = k
        else:
            for k, v in statuses.items():
                if v == child.text:
                    out[child.tag.lower()] = k
        #print("%s: %s" % (child.tag, child.text))
    logger.info("%s" % (out,))
    return out


class HuaweiClient(probe.ProbeClient):

    def save_status(self, status):
        # {'WIFI': 'WIFI_OFF', 'Mode': 'MODE_OFF', 'Signal': '0', 'Roam': 'ROAM_HOME', 'Connect': 'NO_CONNECT', 'Connect6': 'NO_CONNECT', 'SIM': 'SIM_NORMAL', 'Connect4': 'NO_CONNECT'}
        l = location.locator.get_location()
        s = database.DB.get_session()
        t = database.HuaweiTable()
        t.mode = status['mode']
        t.wifi = status['wifi']
        t.roam = status['roam']
        t.connect = status['connect']
        t.connect4 = status['connect4']
        t.connect6 = status['connect6']
        t.signal = status['signal']
        t.elevation = l.ele
        t.lat = l.lat
        t.lon = l.lon
        t.speed = l.speed
        s.add(t)
        s.commit()
        s.close()

    def reconnect(self):
        pass

    def connect(self):
        pass

    def test(self):
        try:
            result = get_signal("http://%s/index/getStatusByAjax.cgi?rid=%s" % (self.address, random.randint(1, 1000)))
        except requests.RequestException:
            logger.debug("Connection failed")
            return
        except Exception:
            logger.exception("Unhandled exception")
            return
        if result:
            self.save_status(result)



if __name__ == '__main__':
    print(get_signal("http://192.168.1.1/index/getStatusByAjax.cgi?rid=1"))