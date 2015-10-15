import os, sys
import socket
import pickle
import time
import binascii

server_name = 'localhost'
server_port = 9000

# States of Sender
WAIT_CALL_0 = 0
WAIT_ACK_0 = 1
WAIT_CALL_1 = 2
WAIT_ACK_0 = 3

class Message:
    def __init__(self, data):
        # Data is an array of 20 char
        self.data = data

class Packet:
    def __init__(self, seqnum, acknum, payload):
        self.seqnum = seqnum # 0 / 1
        self.acknum = acknum # 0 / 1
        self.payload = payload

    def _set_chksum(self, chksum):
        self.chksum = chksum

    def _retrieve_chksum(self):
        tmp = self.chksum
        del self.chksum
        return tmp

class Sender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((server_name, server_port))
        self.state = WAIT_CALL_0

    def _output(self, msg):
        self.sock.send(msg)

    def _close(self):
        self.sock.close()

def calc_chksum(pkt):
    return (binascii.crc32(pkt) & 0xffffffff)

def toggle_bit(bit):
    if bit == 1:
        return 0
    if bit == 0:
        return 1

def create_packet(seq_num, ack_num, payload):
    pkt = Packet(seq_num, ack_num, payload)
    chksum = calc_chksum(pickle.dumps(pkt))
    print 'Checksum size: ', sys.getsizeof(chksum)
    pkt._set_chksum(chksum)
    return pkt

def main():
    start = time.time()
    sender = Sender()

    # TODO: This needs to be properly handled if message is corrupt
    # Destination to save the file to
    dest = sys.argv[2]
    sender._output(dest)

    seq_num = 0
    ack_num = 0

    data = open(sys.argv[1], 'r')
    payload = data.read(32)

    while payload:
        seq_num = toggle_bit(seq_num)
        ack_num = toggle_bit(ack_num)

        print 'Sending'
        print '---'
        print 'Seq_num:', seq_num
        print 'Ack_num:', ack_num
        print '---'

        pkt = create_packet(seq_num, ack_num, payload)
        sender._output(pickle.dumps(pkt))

        print 'Payload size: ', sys.getsizeof(payload)
        print 'Total string size: ', sys.getsizeof(pickle.dumps(pkt))

        payload = data.read(32)

    sender._output('done')
    sender._close()

    print 'Time taken: ', time.time() - start

if __name__ == '__main__':
    main()

