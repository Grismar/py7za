from asyncio import create_task, run, gather, sleep
from queue import Queue, Empty
from subprocess import Popen, PIPE


async def output_parser_7za(proc, q_progress, q_files):
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
            await sleep(0)
        else:
            line += b
    q_progress.put(None)


async def output_printer(q_progress, q_files):
    while True:
        try:
            while True:
                line = q_progress.get_nowait()
                if line is None:
                    return
                print(f'% {line}')
        except Empty:
            pass
        try:
            while True:
                line = q_files.get_nowait()
                print(f'+ {line}')
        except Empty:
            pass
        await sleep(0)


async def run_7za(archive, path):
    zip_proc = Popen([r'../bin/7za.exe', 'a', archive, path, '-bb', '-bso1', '-bse0', '-bsp1'],
                     stdout=PIPE, stderr=PIPE)
    q_progress = Queue()
    q_files = Queue()
    t_parser = create_task(output_parser_7za(zip_proc, q_progress, q_files))
    t_reader = create_task(output_printer(q_progress, q_files))

    await gather(t_parser, t_reader)


async def simple(archive, path):
    p = await create_subprocess_exec(
        r'../bin/7za.exe', 'a', archive, path, '-bb', '-bso1', '-bse0', '-bsp1')

    while p.returncode is None:
        await sleep(1)


run(run_7za('bin.zip', r'D:\0000\server_room_melbourne\\'))
