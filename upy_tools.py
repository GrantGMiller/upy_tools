import network

def macBytes_to_hexstr(bytestr):
    hexChars = []
    for byte in bytestr[3:]:
        h = hex(byte)
        h = str(h)
        h = h.replace('0x', '').upper()
        hexChars.append(h)
    return '-'.join(hexChars)

def auto_setup_wifi_ap():
    '''
    This activates the access point and names is 'uPy:XX-XX-XX' where the XX's are replaced with the last 3 of MAC
    No password for wifi ap.
    :return: None
    '''
    ap = network.WLAN(network.AP_IF)
    mac = ap.config('mac')
    macstr = macBytes_to_hexstr(mac)
    ap.config(essid='uPy:' + macstr)
    ap.config(authmode=0)  # No password

def getsta():
    sta = network.WLAN(network.STA_IF)
    return sta
