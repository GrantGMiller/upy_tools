import http
import network
import time
import auto_setup



Server = http.http_server(80)

while True:
    auto_setup.DoAutoSetup(Server)