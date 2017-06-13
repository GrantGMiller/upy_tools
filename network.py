import random

'''
This module is used for development on a machine not running micropython
'''


AP_IF = 'Wifi Access Point'
STA_IF = 'Wifi Client'

class WLAN:
    def __init__(self, kind):
        self.kind = kind
        self.mac = b'\xa2 \xa6\x12Y}'

    def config(self, paramStr=None, **kwargs):
        if paramStr:
            return getattr(self, paramStr)

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def scan(self):
        if self.kind == STA_IF:
            networks = []
            for i in range(random.randint(5, 10)):
                networkName = b'Network' + str(i).encode()
                otherthing = b'12345'
                channel = i
                db = random.randint(-100, 0)
                type = random.randint(0,5)
                other = 0
                tup = (networkName, otherthing, channel, db, type, other)
                networks.append(tup)
            return networks
        else:
            raise Exception('Only sta can scan')

    def conenct(self):
        pass
