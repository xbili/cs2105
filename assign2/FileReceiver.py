import os, sys
import socket
import pickle

server_name = 'localhost'
server_port = 9001

# States of Receiver
WAIT_CALL_0 = 0
WAIT_CALL_1 = 1

class Packet:
    def __init__(self, seqnum, acknum, checksum, payload):
        self.seqnum = seqnum # 0 / 1
        self.acknum = acknum # 0 / 1
        self.checksum = checksum # Binary string
        self.payload = payload
        self.state = WAIT_CALL_0

class Receiver:
    def __init__(self):
        self.rcv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rcv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rcv_sock.bind(('', server_port))
        print 'Receiving file on', server_port

    def _recv(self, size):
        return self.rcv_sock.recvfrom(size)

    def _close(self):
        self.rcv_sock.close()

def main():
    rcv = Receiver()

    # Receives the first packet which is the file destination
    dest, client_address = rcv._recv(2048)
    f = open(dest, 'w')

    count = 1

    while True:
        pkt_string, client_address = rcv._recv(2048)
        print 'Writing message', count
        pkt = pickle.loads(pkt_string)
        f.write(pkt.payload)
        count+=1
    rcv._close()

if __name__ == '__main__':
    main()

