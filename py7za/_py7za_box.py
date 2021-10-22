from os import remove as os_remove
from logging import error, warning
from conffu import Config
from pathlib import Path
from asyncio import run
from py7za import Py7za, AsyncIOPool, available_cpu_count


async def box(cfg):
    total = 0
    done = False
    current = 0
    running = []
    aiop = AsyncIOPool(pool_size=cfg['cores'] if cfg['cores'] else available_cpu_count())

    cli_options = '' if not cfg['delete'] or cfg['unbox'] else '-sdel '
    cli_options += cfg['7za'] if '7za' in cfg else ''

    def globber(root, glob_expr):
        for fn in Path(root).glob(glob_expr):
            if (fn.is_dir() and cfg['match_dir']) or (fn.is_file() and cfg['match_file']):
                yield fn.relative_to(root).parent, fn.name

    def start(py7za):
        nonlocal running, current
        current += 1
        running.append(py7za)

    async def run_all():
        nonlocal aiop, total, done
        zippers = []
        root = Path(cfg.root).absolute()
        target = Path(cfg.target).absolute() if 'target' in cfg else root
        for sub_path, fn in globber(cfg.root, cfg.glob):
            if cfg['create_folders']:
                (target / sub_path).mkdir(parents=True, exist_ok=True)
            if not cfg['unbox']:
                target_path = target / sub_path / fn if cfg['create_folders'] else target / fn
                if cfg['zip_structure']:
                    content = sub_path / fn
                    wd = str(root)
                else:
                    content = root / sub_path / fn
                    wd = '.'
                zippers.append(
                    Py7za(f'a "{target_path}.zip" "{content}" {cli_options}', on_start=start, working_dir=wd))
            else:
                target_path = target / sub_path if cfg['create_folders'] else target
                zippers.append(Py7za(f'e "{root / sub_path / fn}" -o"{target_path}"', start))
        total = len(zippers)
        async for py7za in aiop.arun_many(zippers):
            if cfg['unbox'] and cfg['delete'] and (py7za.return_code == 0):
                os_remove(py7za.arguments[1])
            running.remove(py7za)
        done = True

    await run_all()


def print_help():
    from _version import __version__
    print(
        '\npy7za-box '+__version__+', command line utility\n'
        '\nPy7za-box ("pizza box") replaces a set of files with individual .zip files\n'
        'containing the originals, or does the reverse by "unboxing" the archives.\n'
        'Py7za uses 7za.exe, more information on the project page.'
        '\n'
        'Use: `py7za-box <glob expression> [options] [7za options]\n'
        '\n'
        '<glob expression>         : A glob expression like "**/*.csv". (required)\n'
        '                            Add quotes if your expression contains spaces.\n'
        'Options:\n'
        '-h/--help                 : This text.\n'
        '-c/--cores <n>            : Try to use specific number of cores. [0 / all]\n'
        '-d/--delete               : Remove the source after (un)boxing. [True]\n'
        '-cf/--create_folders      : Recreate folder structure in target path. [True]\n'
        '-md/--match_dir [bool]    : Glob expression should match dirs. [False]\n'
        '-mf/--match_file [bool]   : Glob expression should match files. [True]\n'
        '-r/--root <path>          : Path glob expression is relative to. ["."]\n'
        '-t/--target <path>        : Root path for output. ["" / in-place]\n'
        '-u/--unbox/--unzip        : Unzip instead of zip (glob to match archives).\n'
        '-v/--verbose              : When provided, show every 7za command executed.\n'
        '-zs/--zip_structure [bool]: Root sub-folder structure is archived. [False]\n'
        '-7/--7za                  : CLI arguments passed to 7za after scripted ones.\n'
        '                            Add quotes if passing more than one argument.\n'
        '\n'
        'Unmatched options will be passed to 7za on the command line.\n'
        '\n'
        'Examples:\n'
        '\n'
        'Zip all .csv files in C:/Data and put the archives in C:/Temp:\n'
        '   py7za-box *.csv --root C:/Data --target C:/Archive\n'
        'Unzip all .csv.zip from C:/Archive and sub-folders in-place:\n'
        '   py7za-box **/*.csv.zip --root C:/Archive --unbox -t C:/Data\n'
        'Zip folders named `Photo*` individally using maximum compression:\n'
        '   py7za-box Photo* -r "C:/My Photos" -md -mf 0 -t C:/Archive -7 "-mx9"'
    )


CLI_DEFAULTS = {
    'cores': 0,
    'delete': True,
    'create_folders': True,
    'match_dir': False,
    'match_file': True,
    'root': '.',
    'unbox': False,
    'verbose': False,
    'zip_structure': False,
    '7za': ''
}


def cli_entry_point():
    cfg = Config.startup(defaults=CLI_DEFAULTS, aliases={
        'h': 'help', 'c': 'cores', 'cf': 'create_folders', 'md': 'match_dir', 'mf': 'match_file', 'u': 'unbox',
        'unzip': 'unbox', 'r': 'root', 'zs': 'zip_structure', 't': 'target', 'v': 'verbose', '7': '7za', 'g': 'glob'
    })

    if cfg.get_as_type('help', bool, False):
        print_help()
        exit(0)

    if len(cfg.arguments['']) != 2 and 'glob' not in cfg:
        error('Missing required single argument glob expression, e.g. `py7za-box *.csv [options]`.')
        print_help()
        exit(1)
    else:
        cfg.glob = cfg.glob if 'glob' in cfg else cfg.arguments[''][1]

    if not Path(cfg.root).is_dir():
        error(f'The provided root directory "{cfg.root}" was not found.')
        exit(2)

    target = cfg.root if 'target' not in cfg or cfg.target is True else cfg.get_as_type('target', str)
    if not Path(target).is_dir():
        error(f'The provided target directory "{cfg.target}" was not found.')
        exit(2)

    if cfg.unbox and cfg.create_folders and 'target' in cfg and not target is True:
        warning(f'When unboxing to a target location (not in-place), original structure cannot be restored '
                f'unless sub-folder from root were included when the archives were created.')

    if cfg.zip_structure and cfg.unbox:
        warning(f'The --zip_structure option was specified, but does not do anything when unboxing and will ignored.')

    if cfg.zip_structure and cfg.create_folders:
        warning(f'Keeping sub-folders from root in archives, as well creating the folder structure in the '
                f'target location may produce unexpected results.')

    run(box(cfg))


if __name__ == '__main__':
    cli_entry_point()
