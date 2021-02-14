from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue, Empty
import ctypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
kernel32.SetConsoleOutputCP(65001)


def output_reader(proc, q):
    for line in iter(proc.stdout.readline, b''):
        q.put(line.decode())


def run_dir(path):
    dir_proc = Popen(['cmd', '/c', 'dir', '/s', path], stdout=PIPE)
    q = Queue()
    t = Thread(target=output_reader, args=(dir_proc, q))
    t.start()

    while dir_proc.poll() is None:
        try:
            line = q.get(block=False)
            print(f'>>{line}', end='')
            if dir_proc.poll() is not None:
                t.join()
                break
        except Empty:
            print('EMPTY')


run_dir(r'C:\Program Files')
