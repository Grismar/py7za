import sys
from pathlib import Path
from asyncio import run, gather, create_task, sleep
from py7za import Py7za, AsyncIOPool


TEST_LOCATION = r'C:\0000\20210407\HN_Scenarios'
FILES_TO_ZIP = '**/*.csv'
TARGET = 'output'


async def main():
    aiop = AsyncIOPool(pool_size=4)
    await aiop.enqueue([Py7za(f'a {TARGET}/{fn.name}.zip {fn}') for fn in Path(TEST_LOCATION).glob(FILES_TO_ZIP)])
    async for task_result in aiop.arun_many():
        print(task_result.arguments, task_result.return_code)


async def alternate():
    async for task_result in AsyncIOPool(pool_size=4).arun_many(
            [Py7za(f'a {TARGET}/{fn.name}.zip {fn}') for fn in Path(TEST_LOCATION).glob(FILES_TO_ZIP)]):
        print(task_result.arguments, task_result.return_code)


async def print_status(pool):
    while True:
        try:
            sys.stdout.write(f'\rstatus: {pool.size}')
        except AttributeError:
            print('stop')
        sys.stdout.flush()
        if pool.size == 0:
            return
        await sleep(0.5)


async def main_with_status():
    aiop = AsyncIOPool(pool_size=4)

    async def run_them():
        async for _ in aiop.arun_many(
                [Py7za(f'a {TARGET}/{fn.name}.zip {fn}') for fn in Path(TEST_LOCATION).glob(FILES_TO_ZIP)]):
            pass

    await gather(run_them(), create_task(print_status(aiop)))


if __name__ == '__main__':
    run(main_with_status())
