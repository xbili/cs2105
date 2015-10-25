###############################################
# This skeleton program is prepared for weak  #
# and average students.                       #
# If you are very strong in programming. DIY! #
# Feel free to modify this program.           #
###############################################

## Alice knows Bob's public key
## Alice sends Bob session (AES) key
## Alice receives messages from Bob, decrypts and saves them to file

import socket
import sys
import pickle
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import random

from AESCipher import AESCipher

# Check if the number of command line argument is 2
if len(sys.argv) != 3:
    exit("Usage: python alice.py <addr> <port>")
else:
    name, ip, port = sys.argv

def main():
    # read Bob's public key from file
    # key is stored using RSA.exportKey and must
    # be read with the respective counterpart
    pub_key = read_public_key()

    # generate AES key using the supplied AESCipher class
    # by providing a 32-byte random string as the password
    sess_key = generate_random_key()

    # encrypt session key using RSA PKCS1_OAEP
    # because RSA can only encode strings and numbers
    # we only need to encode and send the 32-byte random password
    encrypted_sess_key = encrypt_session_key(sess_key, pub_key)
    print 'encrypted_key:', encrypted_key

    # send the session key
    send_session_key()

    # receive the messages
    receive_messages()

def read_public_key():
    f = open('bob-python.pub', 'r')
    return RSA.importKey(f.read())

def generate_random_key():
    raw = random.getrandbits(256)
    return str(raw)

def encrypt_session_key(sess_key, pub_key):
    cipher = PKCS1_OAEP.new(pub_key)
    ciphertext = cipher.encrypt(sess_key)
    return ciphertext

def send_session_key(encrypted_sess_key):
    pass

def receive_messages():
    # because each line is sent by pickling
    # it might be better to read from the socket
    # as a stream and let pickle do its job
    pass

main()
