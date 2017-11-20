import network
import machine

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

def get_ap():
    ap = network.WLAN(network.AP_IF)
    return ap

def getsta():
    sta = network.WLAN(network.STA_IF)
    return sta

def get_mac():
    ap = network.WLAN(network.AP_IF)
    mac = ap.config('mac')
    macstr = macBytes_to_hexstr(mac)
    macstr = macstr.replace('-','')
    return macstr

def _convert_adc_to_volts(adc):
    return (adc/1023) * 3.3

def get_adc(pin):
    value = machine.ADC(pin).read()
    return _convert_adc_to_volts(value)
