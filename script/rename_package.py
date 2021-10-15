from pathlib import Path
from sys import argv
from os import chdir, rename

ORIGINAL = 'python_package'


def replace_name_in(f, new_name):
    content = f.read().replace(ORIGINAL, new_name)
    f.seek(0)
    f.write(content)


def snake_to_pascal(name):
    return ''.join(
        part.lower().capitalize() for part in name.split('_')
    )


def main():
    if len(argv) < 2:
        print(f'Usage: rename.py new_name\nWill rename the "{ORIGINAL}" package to "new_name"')
        exit(1)
    new_name = argv[1]

    # change directory to project root (i.e. the parent of the folder the script is in)
    chdir(Path(__file__).absolute().parent.parent)

    if not Path(ORIGINAL).is_dir():
        print(f'Cannot find directory {ORIGINAL} in {Path(__file__).absolute().parent}')
        exit(2)

    for name in [Path(ORIGINAL) / f'__init__.py',
                 Path('setup.py'),
                 Path('example') / f'hello_world.py',
                 Path('test') / f'test_{ORIGINAL}.py',
                 Path('scripts') / f'rename_package.py',
                 Path('scripts') / f'rename_package.bat']:
        with open(name, 'r', newline='') as f:
            content = f.read().replace(ORIGINAL, new_name).replace(snake_to_pascal(ORIGINAL), snake_to_pascal(new_name))
        with open(name, 'w', newline='') as f:
            f.write(content)

    rename(Path(ORIGINAL) / f'{ORIGINAL}.py', Path(ORIGINAL) / f'{new_name}.py')
    rename(ORIGINAL, new_name)
    rename(Path('test') / f'test_{ORIGINAL}.py', Path('test') / f'test_{new_name}.py')


if __name__ == '__main__':
    main()
