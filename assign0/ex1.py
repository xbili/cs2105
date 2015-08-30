from sys import stdin

def split_into_8(bin):
    return [bin[x:x+8] for x in range(0, len(bin), 8)]

def bit2int(bit):
    return str(int(bit, 2))

def main():
    user_input = stdin.readline().rstrip()
    bit_arr = split_into_8(user_input)
    int_arr = map(bit2int, bit_arr)
    result = reduce(lambda x, y: x + '.' + y, int_arr)
    print result

if __name__ == '__main__':
    main()

