import sys
import operator

def main():
    ops = {
            '+': operator.add,
            '-': operator.sub,
            '/': operator.div,
            '*': operator.mul,
            '**': operator.pow
            }

    args = sys.argv

    if len(args) != 4:
        print "Incorrect number of arguments"
    elif args[2] not in ops.keys():
        print "Invalid inputs"
    elif not args[1].isdigit() or not args[3].isdigit():
        print "Invalid inputs"
    elif args[2] == '/' and args[3] == '0':
        print "Division by zero"
    else:
        print ops[args[2]](int(args[1]), int(args[3]))

if __name__ == '__main__':
    main()

