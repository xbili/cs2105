import os, sys
import socket
import pickle
import time

server_name = 'localhost'
server_port = 9000

class Message:
    def __init__(self, data):
        # Data is an array of 20 char
        self.data = data

class Packet:
    def __init__(self, seqnum, acknum, checksum, payload):
        self.seqnum = seqnum # 0 / 1
        self.acknum = acknum # 0 / 1
        self.checksum = checksum # Binary string
        self.payload = payload

class Sender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((server_name, server_port))

    def _output(self, msg):
        self.sock.send(msg)

    def _close(self):
        self.sock.close()

def toggle_bit(bit):
    if bit == 1:
        return 0
    if bit == 0:
        return 1

def main():
    start = time.time()
    sender = Sender()

    seq_num = 0
    ack_num = 0
    data = open(sys.argv[1], 'r')
    payload = data.read(200)
    pkt = Packet(seq_num, ack_num, '0000000000000000', payload)
    pkt = pickle.dumps(pkt)

    while payload:
        seq_num = toggle_bit(seq_num)
        ack_num = toggle_bit(ack_num)

        # For debug
        print 'Sending'
        print '---'
        print 'seq_num:', seq_num
        print 'ack_num:', ack_num
        print '---'

        pkt = Packet(seq_num, ack_num, '0000000000000000', payload)
        pkt = pickle.dumps(pkt)
        sender._output(pkt)
        payload = data.read(200)

    sender._close()
    print time.time() - start

if __name__ == '__main__':
    main()

