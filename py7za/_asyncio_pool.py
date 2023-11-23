from typing import Union, Awaitable, Iterable, AsyncGenerator, Any, Optional
from asyncio import wait, FIRST_COMPLETED, Queue, QueueEmpty, CancelledError, Task, create_task


class AsyncIOPool:
    def __init__(self, pool_size: int):
        """
        AsyncIOPool manages a queue of awaitables, starting
        :param pool_size:
        """
        self._size = 1
        # assign through setter
        self.size = pool_size

        self._awaitables = Queue()
        self._running = set()
        self._cancelling = False

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value: int):
        if value < 1:
            raise ValueError('AsyncIOPool.size needs to be at least 1')
        self._size = value

    async def enqueue(self, aws: Union[Awaitable, Iterable[Awaitable]]):
        """
        Add one or more awaitables to the queue of awaitable run by arun_many; more can be added while it is running
        :param aws: a single awaitable, or an iterable of awaitables to run
        :return: None
        """
        if self._cancelling:
            raise CancelledError('Cannot enqueue while cancelling')
        if not isinstance(aws, Iterable):
            aws = [aws]
        for aw in aws:
            await self._awaitables.put(aw)

    @staticmethod
    async def _task_wrapper(awaitable):
        return await awaitable

    async def arun_many(self, aws: Optional[Union[Awaitable, Iterable[Awaitable]]] = None) \
            -> AsyncGenerator[Any, None]:
        """
        Run as many tasks as size allows in parallel, starting new ones when previous ones complete
        :param aws: a single awaitable, or an iterable of awaitables to run
        :return: a generator that yields result() from tasks as they complete
        """
        self._cancelling = False
        if aws is not None:
            await self.enqueue(aws)
        self._running = set()
        while True:
            # room for more tasks and tasks queued
            while len(self._running) < self._size and not self._awaitables.empty():
                # add the next task
                t = await self._awaitables.get()
                self._running.add(t if isinstance(t, Task) else create_task(self._task_wrapper(t)))
            else:
                if self._running:
                    # run the current pool of tasks until one or more complete
                    done, self._running = await wait(self._running, return_when=FIRST_COMPLETED)
                    for task in done:
                        try:
                            yield task.result()
                        except CancelledError:
                            if self._cancelling:
                                pass
                            else:
                                raise
            # no more awaitables, then done
            if not self._running and self._awaitables.empty():
                break

    def cancel_all(self):
        self._cancelling = True
        while not self._awaitables.empty():
            try:
                aw = self._awaitables.get_nowait()
            except QueueEmpty:
                break
            if isinstance(aw, Task):
                aw.cancel()
        for t in self._running:
            t.cancel()
