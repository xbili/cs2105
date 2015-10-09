import os, sys
import socket

server_name = 'localhost'
server_port = 9001

def main():
    rcv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rcv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    rcv_sock.bind(('', server_port))

    print 'Receiving file on', server_port
    while True:
        message, client_address = rcv_sock.recvfrom(2048)
        print message
    rcv_sock.close()

if __name__ == '__main__':
    main()

