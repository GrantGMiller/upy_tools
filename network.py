#https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/network_basics.html

# This is meant to emulate the micropython network module so that a develper can write and test code on a PC and then
    #load to a microcontroller at a later time

from random import randint
import socket

STA_IF = 'Wifi Client'
AP_IF  = 'Wifi Access Point'

STAT_GOT_IP = 'STAT_GOT_IP'
STAT_CONNECT_FAIL = 'STAT_CONNECT_FAIL'
STAT_WRONG_PASSWORD = 'STAT_WRONG_PASSWORD'
STAT_NO_AP_FOUND = 'STAT_NO_AP_FOUND'
STAT_IDLE = 'STAT_IDLE'
STAT_CONNECTING = 'STAT_CONNECTING'


my_ip = socket.gethostbyname(socket.gethostname())

class WLAN:
    def __init__(self, kind):
        self._kind = kind
        self._active = False
        self._ssid = None
        self._pw = None
        self._isconnected = None

    def active(self, set_state=None):
        if set_state is None:
            return self._active

        elif isinstance(set_state, bool):
            self._active = set_state

    def connect(self, ssid, pw):
        if self._kind == STA_IF:
            self._ssid = ssid
            self._pw = pw
            self._isconnected = True

    def disconnect(self):
        self._isconnected = False

    def scan(self):
        # https://docs.micropython.org/en/latest/esp8266/library/network.html?highlight=wlan#network.wlan.scan
        if self._kind == STA_IF:
            available_networks = []
            for i in range(5):
                ssid = 'SSID{}'.format(i).encode()
                bssid = '00000000000{}'.format(i)
                rssi = 'rssi{}'.format(i)
                authmode = randint(1, 5 +1)
                hidden = randint(0, 1 +1)

                available_networks.append((ssid, bssid, rssi, authmode, hidden))

            return available_networks

    def status(self):
        possibilities = [
            'STAT_IDLE', #NO CONNECTION or no activity
            'STAT_CONNECTING', # connecting in progress
            'STAT_WRONG_PASSWORD', #failed due to incorrect pw
            'STAT_NO_AP_FOUND', # failed because no ap replied
            'STAT_CONNECT_FAIL', # failed due to other probs
            'STAT_GOT_IP', #successful
        ]

        return possibilities[randint(0, len(possibilities)-1)]

    def isconnected(self):
        return self._isconnected

    def ifconfig(self):
        if self._kind == STA_IF:
            ip = my_ip
            subnet = '255.255.0.0'
            gw = '192.168.0.1'
            dns = '8.8.8.8'

            return (ip, subnet, gw, dns)

        else:
            #This network interface is a wifi client. return the IP assigned by the DNS
            thisIP = socket.gethostbyname(socket.gethostname())
            subnet = '255.255.0.0'
            gw = '192.168.0.1'
            dns = '8.8.8.8'

            return (thisIP, subnet, gw, dns)

