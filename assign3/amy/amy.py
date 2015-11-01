import socket
import sys
import pickle
from Crypto.Hash import MD5
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_PSS
from Crypto.PublicKey import RSA
from Crypto.Random import Fortuna

from AESCipher import AESCipher

if len(sys.argv) != 3:
    exit("Usage: python alice.py <addr> <port>")
else:
    name, ip, port = sys.argv

def main():
    # Setup TCP connection
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    skt.connect((ip, int(port)))

    # Reads public key from the first two packet sent,
    # the only step that is different from part 1
    pub_key = read_public_key(skt)

    # Public key does not match
    if not pub_key:
        print 'Public key is not from Bryan'
        return

    # The regular session key procedure between Bob and Alice
    sess_key = generate_random_key()
    encrypted_sess_key = encrypt_session_key(sess_key, pub_key)
    send_session_key(skt, encrypted_sess_key)
    receive_messages(skt, sess_key)

def read_public_key(skt):
    # Receives public key and MD5 signature
    bryan_public = pickle.loads(skt.recv(1024))
    signature = pickle.loads(skt.recv(1024))

    # Hash Bryan's public key
    hashed_bryan_public = MD5.new()
    hashed_bryan_public.update('bryan')
    hashed_bryan_public.update(bryan_public)

    # Loads berisign public key
    with open('berisign-python.pub', "r") as f:
        berisign_public = RSA.importKey(f.read())

    # Checks if the hash matches
    signer = PKCS1_PSS.new(berisign_public)
    if not signer.verify(hashed_bryan_public, signature):
        print 'Not a valid public key'
        pub = False
    return pub

def generate_random_key():
    generator = Fortuna.FortunaGenerator.AESGenerator()
    generator.reseed('cs2105')
    return generator.pseudo_random_data(32)

def encrypt_session_key(sess_key, pub_key):
    cipher = PKCS1_OAEP.new(pub_key)
    ciphertext = cipher.encrypt(sess_key)
    return ciphertext

def send_session_key(skt, encrypted_sess_key):
    pickled = pickle.dumps(encrypted_sess_key)
    skt.send(pickled)

def receive_messages(skt, sess_key):
    msg = open('msgs.txt', 'w')
    data = skt.recv(1024)
    while data:
        data_arr = split_combined_pickle(data)
        for item in data_arr:
            print item
            if not item is None:
                item = pickle.loads(item)
                cipher = AESCipher(sess_key)
                decrypted = cipher.decrypt(item)
                msg.write(decrypted)
        data = skt.recv(1024) # Fetch next packet
    msg.close()
    skt.close()

def split_combined_pickle(data):
    def append_pic(pic):
        if not pic == '':
            return pic + 'p0\n.'
    return map(append_pic, data.split('p0\n.'))

main()

