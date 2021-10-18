import sys
from asyncio import run, sleep, gather
from py7za import Py7za


async def zip_print(zipper):
    while True:
        sys.stdout.write(f'\r{zipper.progress} [{len(zipper.files)}] last:{zipper.files[-1] if zipper.files else ""}')
        sys.stdout.flush()
        if zipper.done:
            return
        await sleep(0.5)


async def main():
    zipper = Py7za(r'a test.zip C:\Temp')
    print('\n', await gather(zipper, zip_print(zipper)))


if __name__ == '__main__':
    run(main())
