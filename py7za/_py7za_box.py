from logging import error
from conffu import Config
from pathlib import Path


def print_help():
    from _version import __version__
    print(
        '\npy7za-box '+__version__+'\n'
        '\nPy7za-box ("pizza box") replaces a set of files with individual .zip files\n'
        'containing the originals, or reverse the operation by "unboxing" the archives.\n'
        'Py7za uses 7za.exe, more information on the project page.'
        '\n'
        'Use: `py7za-box [options] --glob expression --root path [--verbose] [--unbox]\n'
        '\n'
        'Options:\n'
        '-h/--help         : This text.\n'
        '--glob expression : A glob expression like "**/*.csv" (required).\n'
        '--root path       : Path the glob expression will be relative to.\n'
        '--verbose         : When provided, every 7za command executed will be shown.\n'
        '--unbox           : Unzip instead of zip (glob should match archives).\n'
        '\n'
        'Examples:\n'
        '\n'
        'Zip all .csv files in C:/Data and put the archives in C:/Temp:\n'
        '   py7za-box --glob *.csv --root C:/Data --target C:/Temp\n'
        'Unzip all .csv.zip from C:/Archive and sub-folders in-place:\n'
        '   py7za-box --glob **/*.csv.zip --root C:/Archive --unbox\n'
    )


def cli_entrypoint():
    cfg = Config.startup(defaults={'root': '.', 'unbox': False, 'verbose': False, 'target': None})

    verbose = cfg.get_as_type('verbose', bool, False)
    unbox = cfg.get_as_type('unbox', bool, False)

    if 'glob' not in cfg:
        error('Missing required argument --glob with glob expression, e.g. "--glob *.csv".')
        print_help()
        exit(1)

    if not Path(cfg.root).is_dir():
        error(f'The provided root directory "{cfg.root}" was not found.')
        exit(2)

    target = cfg.root if cfg.target is None else cfg.target
    if not Path(target).is_dir():
        error(f'The provided target directory "{cfg.target}" was not found.')
        exit(2)


if __name__ == '__main__':
    cli_entrypoint()
