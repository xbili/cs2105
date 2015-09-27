import os
import sys
import socket
import thread
import signal

# For handling multiple connections
import select

# For caching
import hashlib

# For Date & Time format
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

# For case insensitive replace
import re

__version__ = '0.0.0'
BUFLEN = 8192
VERSION = 'Python Proxy/' + __version__
HTTPVER = 'HTTP/1.0'

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        self.connected = False
        self.client = connection
        self.client_buffer = ''
        self.timeout = timeout
        self.method, self.path, self.protocol = self.get_base_header()
        if self.method == 'CONNECT':
            self.method_CONNECT()
        elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT',
                             'DELETE', 'TRACE'):
            self.method_others()
        self.client.close()
        if self.connected:
            self.target.close()

    def get_base_header(self):
        while True:
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end != -1:
                break
        print '%s' % self.client_buffer[:end]
        data = (self.client_buffer[:end+1]).split()
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_CONNECT(self):
        self._connect_target(self.path)
        self.client.send(HTTPVER + ' 200 Connection established\n' +
                         'Proxy-agent: %s\n\n' % VERSION)
        self.client_buffer = ''
        self._read_write()

    def method_others(self):
        self.path = self.path[7:]
        i = self.path.find('/')
        host = self.path[:i]
        path = self.path[i:]
        self.connected = self._connect_target(host)
        if self.connected:
            # Conditional Get for Advanced Caching
            conditional = 'If-Modified-Since: ' + self.generate_timestamp() + '\r\n'
            self.client_buffer = conditional + self.client_buffer

            self.target.send('%s %s %s\r\n' % (self.method, path, self.protocol) +
                            self.client_buffer)
            self.client_buffer = ''
            self._read_write()

    def _connect_target(self, host):
        # To handle different ports
        i = host.find(':')
        if i != -1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            port = 80 # Default port 80

        try:
            (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
            self.target = socket.socket(soc_family)
        except Exception:
            # Handles 502
            self._return_502()
            return False

        try:
            self.target.connect(address)
        except Exception:
            # Handles 404
            self._return_404()
            return False

        return True

    def _return_502(self):
        self.client.send('HTTP/1.0 502 Bad Gateway\r\n')
        self.client.send('Content Type: text/html\r\n\r\n')
        self.client.send('Error 502: Bad Gateway')

    def _return_404(self):
        self.client.send('HTTP/1.0 404 Not Found\r\n')
        self.client.send('Content Type: text/html\r\n\r\n')
        self.client.send('Error 404: Not Found')

    def _read_write(self):
        max_timeout = self.timeout / 3
        socs = [self.client, self.target]

        # For caching
        buff = ''
        m = hashlib.md5()
        m.update(self.path)
        cache_filename = m.hexdigest() + '.cached'

        count = 0
        while True:
            count += 1

            # For non-blocking
            (recv, _, error) = select.select(socs, [], [], 3)

            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)

                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        if os.path.exists(cache_filename) and self.check_conditional(data):
                            print 'Cache hit'
                            data = ''.join(open(cache_filename).readlines())
                            data = self.censor_text(data)
                            out.send(data)
                            return
                        print 'Cache miss'
                        buff += data
                        data = self.censor_text(data)
                        out.send(data)
                        count = 0

            if count == max_timeout:
                break

        open(cache_filename, 'wb').writelines(buff)
        buff = ''

    def generate_timestamp(self):
        now = datetime.now()
        stamp = mktime(now.timetuple())
        return format_date_time(stamp)

    def check_conditional(self, data):
        data = data.split('\r\n')[0]
        print data
        if '304' in data:
            return True
        return False

    def censor_text(self, data):
        new_data = ''
        censored_txt = open('censor.txt', 'r').readlines()
        for line in censored_txt:
            print 'line:', line
            data = re.sub(line + '*', '---', data, flags=re.I)
            print 'data:', data
        return data

def start_server(host='localhost', port=8000, timeout=60,
                  handler=ConnectionHandler):
    if len(sys.argv) > 0:
        port = int(sys.argv[1])

    # TCP connection
    soc_type = socket.AF_INET
    soc = socket.socket(soc_type)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((host, port))

    print "Serving on %s:%d." % (host, port)
    soc.listen(0)

    while True:
        thread.start_new_thread(handler, soc.accept() + (timeout,))
        signal.signal(signal.SIGINT, signal_handler)

def signal_handler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    start_server()

