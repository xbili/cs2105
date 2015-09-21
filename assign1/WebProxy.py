import sys
import BaseHTTPServer
import urllib2

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        data = urllib2.urlopen(self.path).readlines()
        self.send_response(200)
        self.end_headers()
        self.wfile.writelines(data)

def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=MyHandler,
        port=8000):

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Listening on port ' + str(port)
    httpd.serve_forever()

if __name__ == '__main__':
    args = sys.argv
    run(port = int(args[1]))

