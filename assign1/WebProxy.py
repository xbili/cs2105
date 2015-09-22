import sys
import socket
import thread
import select

__version__ = '0.0.0'
BUFLEN = 8192
VERSION = 'Python Proxy/' + __version__
HTTPVER = 'HTTP/1.0'

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
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
        self._connect_target(host)
        self.target.send('%s %s %s\n' % (self.method, path, self.protocol) +
                         self.client_buffer)
        self.client_buffer = ''
        self._read_write()

    def _connect_target(self, host):
        i = host.find(':')
        if i != -1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            port = 80
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family)
        self.target.connect(address)

    def _read_write(self):
        max_timeout = self.timeout / 3
        socs = [self.client, self.target]
        count = 0
        while True:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
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
                        out.send(data)
                        count = 0
            if count == max_timeout:
                break

def start_server(host='localhost', port=8080, timeout=60,
                  handler=ConnectionHandler):
    if len(sys.argv) > 0:
        port = int(sys.argv[1])

    soc_type = socket.AF_INET
    soc = socket.socket(soc_type)
    soc.bind((host, port))
    print "Serving on %s:%d." % (host, port)
    soc.listen(0)
    while True:
        thread.start_new_thread(handler, soc.accept() + (timeout,))

if __name__ == '__main__':
    start_server()

