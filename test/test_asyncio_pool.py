import unittest
from asyncio import sleep
from random import random
from py7za.py7za_box import AsyncIOPool


class AwaitableCounter:
    number_running = 0
    completed = 0

    def __init__(self, n, t=.01, rnd=True):
        self.rnd = rnd
        self.t = t
        self.n = n
        self.running = False

    def __await__(self):
        return self.arun().__await__()

    def close(self):
        if self.running:
            self.number_running -= 1
            self.running = False

    async def arun(self) -> 'AwaitableCounter':
        self.running = True
        self.number_running += 1
        while self.n > 0:
            self.n -= 1
            await sleep(self.t if not self.rnd else self.t * 2 * random())
        self.completed += 1
        self.number_running -= 1
        return self


class TestPy7zaBox(unittest.IsolatedAsyncioTestCase):
    async def test_aiop(self):
        c, n, total = 0, 5, 100
        aiop = AsyncIOPool(n)
        tasks = [AwaitableCounter(10) for __ in range(total)]
        done = []
        s = 0
        async for t in aiop.arun_many(tasks):
            done.append(t)
            self.assertLess(AwaitableCounter.number_running, n, f'never more than pool size running')
            s += AwaitableCounter.number_running
            c += 1
        self.assertGreater(c, 2, 'test sufficient to at least run 3 cycles')
        self.assertEqual(len(done), total, 'all tasks completed')
        print(s/c)

    async def test_aiop_size(self):
        with self.assertRaises(ValueError):
            __ = AsyncIOPool(0)

    async def test_aiop_cancel(self):
        n = 4
        aiop = AsyncIOPool(n)
        tasks = [AwaitableCounter(10) for __ in range(10)]
        async for __ in aiop.arun_many(tasks):
            aiop.cancel_all()
        self.assertEqual(AwaitableCounter.number_running, 0, 'no more running tasks')
        self.assertLess(AwaitableCounter.completed, 4, 'at most 4 completed')
