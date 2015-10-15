import os, sys
import socket
import pickle
import binascii

server_name = 'localhost'
server_port = int(sys.argv[1])

# States of Receiver
WAIT_CALL_0 = 0
WAIT_CALL_1 = 1

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

class Receiver:
    def __init__(self):
        self.rcv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rcv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rcv_sock.bind(('', server_port))
        print 'Receiving file on', server_port

    def _output(self, msg, addr):
        self.rcv_sock.sendto(msg, addr)

    def _recv(self, size):
        return self.rcv_sock.recvfrom(size)

    def _close(self):
        self.rcv_sock.close()

def verify_chksum(pkt):
    return (binascii.crc32(pkt) & 0xffffffff)

def is_corrupt(pkt):
    chksum = pkt._retrieve_chksum()
    print 'Expected checksum:', chksum
    print 'Actual checksum:', verify_chksum(pickle.dumps(pkt))
    return chksum != verify_chksum(pickle.dumps(pkt))

def create_packet(seq_num, ack_num, payload):
    pkt = Packet(seq_num, ack_num, payload)
    chksum = verify_chksum(pickle.dumps(pkt))
    print 'Checksum size: ', sys.getsizeof(chksum)
    pkt._set_chksum(chksum)
    return pkt

def main():
    rcv = Receiver()
    dest_pkt, client_address = rcv._recv(4096)
    dest = pickle.loads(dest_pkt)
    f = open(dest.payload, 'wb')

    count = 1
    while True:
        pkt_string, client_address = rcv._recv(4096)

        if pkt_string == 'done':
            f.close()
        else:
            try:
                pkt = pickle.loads(pkt_string)
                if is_corrupt(pkt):
                    print 'Corrupted'
                    nak = create_packet(0, 0, 'ack')
                    rcv._output(pickle.dumps(nak), client_address)
                else:
                    print 'Writing message', count
                    f.write(pkt.payload)
                    count+=1
            except:
                print 'Entire Packet Corrupted'
                nak = create_packet(0, 0, '')
                rcv._output(pickle.dumps(nak), client_address)
    rcv._close()

if __name__ == '__main__':
    main()

