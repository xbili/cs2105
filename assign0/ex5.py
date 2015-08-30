import sys
from sys import stdin

class Fields:
    def __init__(self):
        self.value = {}

    def add_pair(self, key, value):
        if key not in self.value.keys():
            self.value[key] = value

    def parse_string(self, str):
        pair = str.split(':')
        if len(pair) > 2:
            print 'Invalid input'
        else:
            return map(lambda x: x.strip(), pair)

    def is_input(self, str):
        return ':' in str

    def get_value(self, key):
        try:
            return self.value[key]
        except KeyError:
            return 'Unknown field'

def main():
    fields = Fields()

    end = False
    mode = 'add'
    while not end:
        user_input = stdin.readline().strip()

        if user_input == '':
            mode = 'get'
        elif mode == 'add':
            pair = fields.parse_string(user_input)
            fields.add_pair(pair[0], pair[1])
        elif user_input == 'quit' and mode == 'get':
            end = True
        else:
            print fields.get_value(user_input)

if __name__ == '__main__':
    main()

