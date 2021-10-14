from pathlib import Path
from asyncio import run, gather
from py7za import Py7za, AsyncIOPool


async def main():
    aiop = AsyncIOPool(size=4)
    await aiop.enqueue([Py7za(f'a output/{fn.name}.zip {fn}') for fn in Path(r'C:\0000').glob('**/*.csv')])
    async for x in aiop.arun_many():
        print(x.arguments, x.return_code)


if __name__ == '__main__':
    run(main())
