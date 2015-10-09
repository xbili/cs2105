import os, sys
from socket import *

server_name = 'localhost'
server_port = 9001

def main():
    rcv_sock = socket(AF_INET, SOCK_DGRAM)
    socket.bind(rcv_sock, ('', server_port))
    print 'Receiving file on', server_port
    while True:
        message, client_address = rcv_sock.recvfrom(2048)
        print message
    socket.close(rcv_sock)

if __name__ == '__main__':
    main()

