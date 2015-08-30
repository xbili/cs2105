import sys
import time
from subprocess import PIPE, Popen
from threading import Thread
from Queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, ''):
        queue.put(line)
    out.close()

def main():
    p = Popen(['python', 'lis.py'], stdout=PIPE, bufsize=1, shell=False, close_fds=ON_POSIX)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True
    t.start()

    output = sys.argv[1]
    start_time = int(sys.argv[2])
    interval = int(sys.argv[3])

    time.sleep(start_time)

    while True:
        try:
            line = q.get_nowait()
        except Empty:
            print output
            time.sleep(interval)
        else:
            if line.strip() == 'q':
                exit()

if __name__ == '__main__':
    main()

