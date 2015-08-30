import sys
import binascii

def CRC32_from_file(filename):
    buf = open(filename, 'rb').read()
    return (binascii.crc32(buf) & 0xffffffff)

def main():
    filename = sys.argv[1];
    print CRC32_from_file(filename)

if __name__ == '__main__':
    main()

