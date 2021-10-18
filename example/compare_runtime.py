from pathlib import Path
from asyncio import run
from py7za import Py7za, AsyncIOPool, available_cpu_count
from timeit import timeit
from os import remove


TEST_LOCATION = r'C:\0000\20210407\HN_Scenarios'
FILES_TO_ZIP = '*.csv'
TARGET = 'output'


def clean_output():
    for fn in Path(TARGET).glob('*.zip'):
        remove(fn)


async def run_pool(pool_size):
    async for __ in AsyncIOPool(pool_size).arun_many(
            [Py7za(f'a {TARGET}/{fn.name}.zip {fn}') for fn in Path(TEST_LOCATION).glob(f'**/{FILES_TO_ZIP}')]):
        pass


def main():
    results = {}
    repeats = 3
    for n in range(1, available_cpu_count()+1):
        results[n] = 0
        for __ in range(repeats):
            clean_output()
            results[n] += timeit(lambda: run(run_pool(n)), number=1)
        results[n] /= repeats
        print(f'Average runtime over {repeats} runs in pool size {n}: {results[n]:.3f}')


if __name__ == '__main__':
    main()
