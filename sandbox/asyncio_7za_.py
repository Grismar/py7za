from asyncio import create_subprocess_exec, Queue, QueueEmpty, create_task, run, gather, sleep
from asyncio.subprocess import PIPE


async def stdout_parser(proc, my_queue):
    while True:
        b = await proc.stdout.read(1)
        await my_queue.put(b)
        # stdout read will return b'' when the process has ended
        if b == b'':
            return


async def reader(my_queue):
    while True:
        try:
            b = await my_queue.get()
            if b == b'':
                return
            print(b.decode(), end='')
        except QueueEmpty:
            pass


async def main():
    p = await create_subprocess_exec(
        '..\\bin\\7za.exe', 'a', 'bin.zip', r'D:\0000\server_room_melbourne\\', '-bb', '-bsp1', stdout=PIPE)
    my_queue = Queue()
    t_parser = create_task(stdout_parser(p, my_queue))
    t_reader = create_task(reader(my_queue))

    await gather(t_parser, t_reader)


run(main())
