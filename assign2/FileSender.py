import os, sys
import io
import socket

server_name = 'localhost'
server_port = 9000

def main():
    sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sender_sock.connect((server_name, server_port))

    data = open(sys.argv[1], 'r')
    pkt = data.read(1024)
    while (pkt):
        print 'Sending'
        sender_sock.send(pkt)
        pkt = data.read(1024)

    sender_sock.close()

if __name__ == '__main__':
    main()

