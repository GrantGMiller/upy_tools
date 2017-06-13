import socket

http_response_header = '''HTTP/1.1 200 OK
Content-Type: text/html
Connection: close
'''


class http_server:
    def __init__(self, port, interface):
        '''
        Starts a http server to handle incoming request.
        :param port:
        :param interface:
        '''
        self.interface = interface

        self.port = port
        self.s = socket.socket()
        self.addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
        self.s.bind(self.addr)
        self.s.listen(1)
        self.s.settimeout(1)  # wait for X seconds for a new request to come in.
        # The int parameter in s.listen(int) is the number of connections to queue up before rejecting more connections.
        # Since HTTP makes/breaks connection per request/response pair, this number can be relatively low.

    def process_a_request(self):
        '''
        This method will see if there is a request to process.
        This method must be called regularly from the main.py to serve pages properly.
        :return: http_request object or None if no request was received.
        '''
        try:
            client, addr = self.s.accept()
        except Exception as e:
            print(e)
            return None

        # If we got here, then we received a socket connection
        print(addr, 'Connected')

        # return a request object.
        cfile = client.makefile('rwb', 0)
        req_raw = ''

        recv_len = 1024
        while True:
            recv = client.recv(1024)
            req_raw += recv.decode()

            if len(recv) < recv_len:
                break

        req = http_request(req_raw, client)
        return req


class http_request:
    def __init__(self, raw, client):
        self.raw = raw
        print('http_request raw=', self.raw)
        self.client = client

        self.lines = raw.split('\r\n')
        self.nvps = {}  # name-value-pairs = {'name': 'value'}
        self._parse_nvps()

    def _parse_nvps(self):
        for line in self.lines:
            try:
                if '=' in line:
                    space_split = line.split(' ')
                    for chunk in space_split:
                        if '=' in chunk:
                            chunk = chunk.replace('?', '')
                            chunk = chunk.replace('/', '')

                            pairs = chunk.split('&')
                            for pair in pairs:
                                name, value = pair.split('=')
                                self.nvps[name] = value
                                print('NVP Found: {}={}'.format(name, value))
            except Exception as e:
                print('Error parsing nvp. \nline={}\nError: {}'.format(line, e))

    def get_value(self, name):
        if name in self.nvps:
            return self.nvps[name]
        else:
            return None

    def get_nvps(self):
        return self.nvps

    def send_response(self, resp):
        resp_raw = resp.get_raw()
        self.client.send(resp_raw.encode())
        # self.client.close()
        print('resposne sent')


class http_response:
    def __init__(self):
        self.header = http_response_header
        self.body = '<html><body>This is the body</body></html>'
        self.raw = ''

    def get_raw(self):
        self._compile_response()
        print('http_response raw=', self.raw)
        return self.raw

    def set_body(self, body):
        self.body = body

    def _compile_response(self):
        self.raw = ''
        self.raw += self.header
        self.raw += '\r\n'  # Needed to separate header and body
        self.raw += self.body
        self.raw += '\r\n'

    def add_redirect(self, url):
        start_phrase = '<html>'
        start_index = self.body.find(start_phrase) + len(start_phrase)
        end_index = start_index
        # script = '''<meta http-equiv="refresh" content="0; url=http:{}" />\r\n'''.format(url) #html
        script = '''<script>window.location="{}"</script>'''.format(url)  # javascript
        self.body = self.body[:start_index] + script + self.body[end_index:]
