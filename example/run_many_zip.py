import sys
from pathlib import Path
from asyncio import run, gather, create_task, sleep
from py7za import Py7za, AsyncIOPool
from conffu import Config

cfg = Config.startup()
TEST_LOCATION = r'../scripts' if 'root' not in cfg else cfg.root
FILES_TO_ZIP = '*.bat' if 'glob' not in cfg else cfg.glob
TARGET = 'output' if 'target' not in cfg else cfg.target


async def main():
    aiop = AsyncIOPool(pool_size=4)
    await aiop.enqueue([Py7za(f'a {TARGET}/{fn.name}.zip {fn}') for fn in Path(TEST_LOCATION).glob(FILES_TO_ZIP)])
    async for task_result in aiop.arun_many():
        print(task_result.arguments, task_result.return_code)


async def alternate():
    async for task_result in AsyncIOPool(pool_size=4).arun_many(
            [Py7za(f'a {TARGET}/{fn.name}.zip {fn}') for fn in Path(TEST_LOCATION).glob(FILES_TO_ZIP)]):
        print(task_result.arguments, task_result.return_code)


async def main_with_status():
    aiop = AsyncIOPool(pool_size=4)
    running = []
    total = 0
    current = 0
    done = False

    def globber(root, glob_expr):
        for fn in Path(root).glob(glob_expr):
            yield fn.relative_to(root).parent, fn.name

    def start(py7za):
        nonlocal running, current
        current += 1
        running.append(py7za)

    async def print_status():
        nonlocal done, running, current, total
        while True:
            sys.stdout.write(f'\rstatus: {current}/{total} ... '
                             f'{" ".join([f"{str(py7za.progress)}/100%" for py7za in running if py7za.progress])}')
            if done:
                return
            await sleep(0.5)

    async def run_them():
        nonlocal done, running, total
        zippers = []
        test_location = Path(TEST_LOCATION).absolute()
        target = Path(TARGET).absolute()
        for p, fn in globber(TEST_LOCATION, FILES_TO_ZIP):
            if not (target / p).is_dir():
                (target / p).mkdir(parents=True)
            zippers.append(Py7za(f'a "{target / p / fn}.zip" "{test_location / p / fn}"', start))
        total = len(zippers)
        if total > 0:
            async for py7za in aiop.arun_many(zippers):
                running.remove(py7za)
        done = True

    await gather(run_them(), print_status())


if __name__ == '__main__':
    run(main_with_status())
