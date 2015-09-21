import sys
import shutil

def main():
    src = sys.argv[1]
    dst = sys.argv[2]
    try:
        shutil.copyfile(src, dst)
        print src + ' successfully copied to ' + dst
    except IOError:
        print 'File not found'

if __name__ == '__main__':
    main()

