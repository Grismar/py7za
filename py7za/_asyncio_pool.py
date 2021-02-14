from typing import Union, Callable, List, Generator, Any
from asyncio import wait, FIRST_COMPLETED, Queue, QueueEmpty


class AsyncIOPool:
    def __init__(self, size: int):
        self._size = 1
        # assign through setter
        self.size = size

        self._tasks = Queue()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value: int):
        if value < 1:
            raise ValueError('AsyncIOPool.size needs to be at least 1')
        self._size = value

    async def enqueue(self, task: Union[Callable, List[Callable]]):
        if isinstance(task, list):
            for t in task:
                await self._tasks.put(t)
        else:
            await self._tasks.put(task)

    async def arun_many(self) -> Generator[Any, None, None]:
        """
        Run as many tasks as size allows in parallel, starting new ones when previous ones complete
        :return: a generator that yields the results from the tasks as they complete
        """
        aws = set()
        while True:
            # room for more tasks and tasks queued
            while len(aws) < self._size and not self._tasks.empty():
                # add the next task
                aws.add(await self._tasks.get())
            else:
                # run the current pool of tasks until one completes
                done, aws = await wait(aws, return_when=FIRST_COMPLETED)
                for task in done:
                    yield task.result()
            # no more awaitables, then done
            if not aws and self._tasks.empty():
                break
