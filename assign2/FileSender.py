import os, sys
import socket
import cPickle as pickle
import time
import binascii
import zlib

server_name = sys.argv[1]
server_port = int(sys.argv[2])

TIMEOUT = 0.001
PAYLOAD_SIZE = 512

# States of Sender
WAIT_CALL_0 = 0
WAIT_ACK_0 = 1
WAIT_CALL_1 = 2
WAIT_ACK_1 = 3

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

    def _set_timeout(self, timeout):
        self.sock.settimeout(TIMEOUT)

    def _recv(self, size):
        return self.sock.recvfrom(size)

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
    # print 'Checksum size: ', sys.getsizeof(chksum)
    pkt._set_chksum(chksum)
    return pkt

def is_corrupt(pkt):
    try:
        pkt = pickle.loads(pkt)
        chksum = pkt._retrieve_chksum()
        # print 'Expected checksum:', chksum
        # print 'Actual checksum:', calc_chksum(pickle.dumps(pkt))
        return chksum != calc_chksum(pickle.dumps(pkt))
    except:
        return True

def is_ack(pkt, num):
    pkt = pickle.loads(pkt)
    acknum = get_ack_num(pkt)
    payload = pkt.payload
    return payload == 'ack' and acknum == num

def get_ack_num(pkt):
    return pkt.acknum

def wait_ack_handler(sender, acknum, payload):
    seq_num = acknum
    while True:
        try:
            sender._set_timeout(0.1)
            pkt_string, client_address = sender._recv(4096)

            if is_corrupt(pkt_string) or is_ack(pkt_string, toggle_bit(acknum)):
                pkt = create_packet(seq_num, acknum, payload)
                compressed_pkt = zlib.compress(pickle.dumps(pkt))
                sender._output(compressed_pkt)
            elif not is_corrupt(pkt_string) and is_ack(pkt_string, acknum):
                if acknum == 0:
                    sender.state = WAIT_CALL_1
                else:
                    sender.state = WAIT_CALL_0
                return
        except socket.timeout:
            # print 'Timed out'
            pkt = create_packet(seq_num, acknum, payload)
            compressed_pkt = zlib.compress(pickle.dumps(pkt))
            sender._output(compressed_pkt)


def main():
    start = time.time()
    sender = Sender()

    seq_num = 0
    ack_num = 0

    data = open(sys.argv[3], 'r')
    payload = 'dest: ' + sys.argv[4]
    next_packet = True

    count = 1
    while next_packet:
        if sender.state == WAIT_CALL_0:
            if count > 1:
                sender._set_timeout(None)
            seq_num = 0
            pkt = create_packet(seq_num, ack_num, payload)
            compressed_pkt = zlib.compress(pickle.dumps(pkt))
            sender._output(compressed_pkt)

            count+=1
            # print 'Sent packet', count

            sender.state = WAIT_ACK_0
        elif sender.state == WAIT_ACK_0:
            wait_ack_handler(sender, 0, payload)
            payload = data.read(PAYLOAD_SIZE)
            # print 'ack 0 received'
        elif sender.state == WAIT_CALL_1:
            sender._set_timeout(None)
            seq_num = 1
            pkt = create_packet(seq_num, ack_num, payload)
            compressed_pkt = zlib.compress(pickle.dumps(pkt))
            sender._output(compressed_pkt)

            count+=1
            # print 'Sent packet', count

            sender.state = WAIT_ACK_1
        elif sender.state == WAIT_ACK_1:
            wait_ack_handler(sender, 1, payload)
            payload = data.read(PAYLOAD_SIZE)
            # print 'ack 1 received'
        # print sender.state

        if payload == '':
            next_packet = False

    sender._close()

    print 'Time taken: ', time.time() - start

if __name__ == '__main__':
    main()

