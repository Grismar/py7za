from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue, Empty


def output_parser_7za(proc, q_progress, q_files):
    line = b''
    # stdout read will only return b'' when the process has ended
    while (b := proc.stdout.read(1)) != b'':
        # 7za outputs \r (CR) as end of line
        if b == b'\r':
            parts = line.decode().split()
            # if there was anything on the line
            if len(parts) > 0:
                # if the first part is a progress indicator
                if parts[0][-1] == '%':
                    q_progress.put(int(parts[0][:-1]))
                # if the first part indicates an added or updated file
                elif parts[0] in '+U':
                    q_files.put((parts[0], line[2:]))
            line = b''
        else:
            line += b


def run_7za(archive, path):
    zip_proc = Popen([r'../bin/7za.exe', 'a', archive, path, '-bb', '-bso1', '-bse0', '-bsp1'],
                     stdout=PIPE, stderr=PIPE)
    q_progress = Queue()
    q_files = Queue()
    t = Thread(target=output_parser_7za, args=(zip_proc, q_progress, q_files))
    t.start()

    while zip_proc.poll() is None:
        try:
            line = q_progress.get(block=False)
            print(f'% {line}')
        except Empty:
            pass
        try:
            line = q_files.get(block=False)
            print(f'+ {line}')
        except Empty:
            pass
    t.join()


run_7za('bin.zip', r'C:\0000\result_k80_local_write')
