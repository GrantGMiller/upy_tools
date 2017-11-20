import http
import network
import time


def DoAutoSetup(server):
    ap = network.WLAN(network.AP_IF)
    sta = network.WLAN(network.STA_IF)


    Request = server.process_a_request()
    print('Request=', Request)

    if Request is not None:
        disable_wifi_ap = Request.get_value('disable_wifi_ap')
        ssid = Request.get_value('nm')
        if ssid:
            # the user is trying to connect to a network
            pw = Request.get_value('pw')
            my_ip = ap.ifconfig()[0]

            if sta.active() is not True:
                sta.active(True)

            sta.connect(ssid, pw)
            count = 0
            while sta.status() not in [
                network.STAT_GOT_IP,
                network.STAT_CONNECT_FAIL,
                network.STAT_WRONG_PASSWORD,
                network.STAT_NO_AP_FOUND,
            ]:
                count += 1
                time.sleep(1)
                if count > 10:
                    break

            result = sta.status()
            if result == network.STAT_GOT_IP:
                result = 'STAT_GOT_IP'
            elif result == network.STAT_IDLE:
                result = 'STAT_IDLE'
            elif result == network.STAT_CONNECTING:
                result = 'STAT_CONNECTING'
            elif result == network.STAT_WRONG_PASSWORD:
                result = 'STAT_WRONG_PASSWORD'
            elif result == network.STAT_NO_AP_FOUND:
                result = 'STAT_NO_AP_FOUND'
            elif result == network.STAT_CONNECT_FAIL:
                result = 'STAT_CONNECT_FAIL'
            else:
                result = 'ELSE'

            Response = http.http_response()
            Response.set_body(
                '<html><body>Trying to connect to {}<br>Result: {}<br><br><a href="http://{}">Connect to a different network</a><br><a href="http://{}?disable_wifi_ap=true&ssidKill={}">Disable wifi access point</a></body></html>'.format(
                    ssid, result, my_ip, my_ip, ssid))
            Request.send_response(Response)
        elif disable_wifi_ap is not None:
            Response = http.http_response()
            ssid = Request.get_value('ssidKill')
            Response.set_body(
                '<html><body>Wifi AP is now disabled.<br>Connect to the network "{}", then <a href="http://{}">click here</a></body></html>'.format(
                    ssid, sta.ifconfig()[0]))
            Request.send_response(Response)

            time.sleep(5)
            if disable_wifi_ap.upper() == 'TRUE':
                ap.active(False)


        else:
            # present the user with available networks to connect to

            Response = http.http_response()

            html = '<body><html><h1>Welcome to Micropython</h1><br><form method="POST">Select a network:<select name="nm">'

            if sta.active() is not True:
                sta.active(True)

            for net_info in sta.scan():
                html += '<option>{}</option>'.format(net_info[0].decode())

            html += '</select><br>Password:<input type="password" name="pw"><br><input type="submit" value="Connect Now"></form></body></html>'
            Response.set_body(html)

            Request.send_response(Response)
