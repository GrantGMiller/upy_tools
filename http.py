import socket
import sys

http_response_header = '''HTTP/1.1 200 OK
Content-Type: text/html
Connection: close
'''

def urlencode(d):
    #d = dict
    nvps = []
    for k in d:
        nvps.append('{}={}'.format(k, d[k]))

    result = '&'.join(nvps)
    return result

class http_server:
    def __init__(self, port, interface=None):
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
            client.settimeout(10)
        except Exception as e:
            #print(e)
            return None

        # If we got here, then we received a socket connection
        print(addr, 'Connected')

        # return a request object.
        cfile = client.makefile('rwb', 0)
        req_raw = ''

        recv_len = 1024
        while True:
            recv = client.recv(2048)
            req_raw += recv.decode()

            if len(recv) < recv_len:
                break

        req = http_request(raw=req_raw, client=client)
        return req


class http_request:
    def __init__(self, url=None, data=None, raw=None, client=None,):
        '''

        :param url: #url to send the request to with self.send()
        :param data: #dict holding any data that you would like to pass in the request body. This will be urlencoded
        :param raw: #the raw HTTP request
        :param client: #The socket to send the request to. Default None means a new socket will be created when self.send()
        '''
        self.url = url #Should include 'http://...'
        self.host = 'www.host.com' #placeholder
        self.page = '/'
        self.body = ''

        self.data = data
        if data:
            self.method = 'POST'
        else:
            self.method = 'GET'

        if isinstance(data, dict):
            self.body += urlencode(data) + '\r\n'
            print('req.body=', self.body)

        if self.url:
            afterHTTP = self.url.split('//')[-1]
            self.host = afterHTTP.split('/')[0]
            self.page = afterHTTP.replace(self.host, '')
            if self.page == '':
                self.page = '/'

            self.header = '''{} {} HTTP/1.1\r\nHost: {}\r\nUser-Agent: Micropython\r\n'''.format(self.method, self.page, self.host)

        self.raw = raw
        if self.raw:
            print('http_request raw=', self.raw)
        self.client = client

        self.nvps = {}  # name-value-pairs = {'name': 'value'}
        self.headers = {}

        self._parse_nvps()

    def add_header(self, name, value):
        self.headers[name] = value
        self.header += '''{}: {}\r\n'''.format(name, value)

    def set_body(self, body):
        self.body = body

    def _parse_nvps(self):
        if self.raw:
            lines = self.raw.split('\r\n')
            for line in lines:
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
                    print('Error parsing nvp. \nline={}\nError: {}\n'.format(line, e))
                    try:
                        print('pair=', pair)
                    except:
                        pass

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
        if sys.platform == 'esp8266':
            self.client.close()
        else:
            pass
        print('resposne sent')

    def send(self):
        '''
        Sends a HTTP request to self.url with self.data attached
        '''
        print('req.send()')
        print('self.header=', self.header)
        print('self.body=', self.body)
        self.raw = self.header
        self.raw += '\r\n'
        self.raw += self.body
        self.raw += '\r\n'
        print('req.raw=', self.raw.encode())
        s = socket.socket()
        s.settimeout(10)
        #try:
        addr = socket.getaddrinfo(self.host, 80)[0][-1]
        s.connect(addr)
        s.send(self.raw.encode())

        resp_raw = ''
        recv_len = 1024
        while True:
            recv = s.recv(1024)
            resp_raw += recv.decode()

            if len(recv) < recv_len:
                break
        s.close()

        return http_response(raw=resp_raw)
        #except Exception as e:
            #print('http.request.send Exception:', e)
            #return None



class http_response:
    def __init__(self, raw=''):
        self.header = http_response_header
        self.body = '<html><body>This is the body</body></html>'
        if isinstance(raw, bytes):
            raw = raw.decode()
        self.raw = raw
        self.headers = {}

        self._parse_headers()

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

    def _parse_headers(self):
        lines = self.raw.split('\r\n')
        for line in lines:
            if ':' in line:
                try:
                    name, value = line.split(': ')
                    self.headers[name] = value
                except:
                    pass

    def get_header(self, name):
        if name in self.headers:
            return self.headers[name]
        else:
            return None
