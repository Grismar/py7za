from asyncio import run, sleep, gather
from py7za import AsyncIOPool
from random import randint


async def roll_even(n, ap):
    roll = 1
    while roll % 2 == 1:
        roll = randint(1, 6)
        print(f'DIE {n} ROLLED {roll}')
        if roll == 5:
            ap.n = ap.n + 1
            print(f'FIVE ON {n}, ADDING DIE {ap.n}')
            await ap.enqueue(roll_even(ap.n, ap))
        if roll % 2 == 1:
            print(f'ODD ON {n}, ROLLING IT AGAIN')
    return n, roll


async def run_all():
    ap = AsyncIOPool(2)
    await ap.enqueue([roll_even(n, ap) for n in range(1, 5)])
    ap.n = 4
    async for x in ap.arun_many():
        print(f'EVEN RESULT {x}')

run(run_all())
