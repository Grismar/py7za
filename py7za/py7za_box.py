from shlex import split
from sys import stdout
from os import remove as os_remove, stat, name as os_name
from datetime import datetime, timezone
import logging
from logging import error, warning, info
from conffu import Config
from pathlib import Path
from asyncio import get_event_loop, sleep, gather
from py7za import Py7za, AsyncIOPool, available_cpu_count, nice_size
from subprocess import list2cmdline
import re
from json import load
from json.decoder import JSONDecodeError
from typing import Optional
# only used for status
from zipfile import ZipFile

ARCHIVE_SUFFIXES = ['.zip', '.zipx', '.gz', '.7z', '.s7z', '.lzma', '.lz', '.cab', '.jar', '.war', '.rar']

aiop: Optional[AsyncIOPool] = None


async def box(cfg):
    global aiop

    start_time = datetime.now()
    total = 0
    done = False
    skipped = 0
    finished = 0
    total_content_size = 0
    total_zip_size = 0
    current = 0
    running = []

    if 'regex' in cfg:
        try:
            regex = re.compile(cfg.regex)
        except re.error:
            error(f'Invalid regex pattern: "{cfg.regex}"')
            exit(1)
    else:
        regex = False

    parallel = 0
    try:
        if isinstance(cfg['parallel'], str) and cfg['parallel'] and cfg['parallel'][-1].lower() == 'x':
            parallel = int(cfg['parallel'][:-1]) * available_cpu_count()
        else:
            parallel = int(cfg['parallel'])
    except ValueError:
        error(f'Invalid value for --parallel: {cfg["parallel"]}')
        exit(1)
    if parallel == 0:
        parallel = available_cpu_count()
    aiop = AsyncIOPool(pool_size=parallel)

    cli_options = '-y '
    cli_options += '-sdel ' if cfg['delete'] and not cfg['unbox'] else ''
    cli_options += f'-ao{cfg.overwrite} ' if cfg['unbox'] else ''
    cli_options += cfg['7za'] if '7za' in cfg else ''
    types = [o for o in split(cli_options) if o.startswith('-t')]
    if len(types) > 1:
        error(f'Cannot provide multiple archive types to 7za: {types}')
        exit(1)
    elif len(types) == 0:
        cfg.suffix = '.7z'
    else:
        cfg.suffix = f'.{types[0][2:]}'

    print_result = cfg.output in 'dlv'
    info_command = cfg.output == 'v'
    level = logging.INFO if info_command else logging.WARNING
    if 'log_error' in cfg:
        # only log to file
        logging.basicConfig(
            level=level, format='%(asctime)s %(levelname)s %(message)s', filename=cfg.log_error, filemode='a')
    else:
        # only log to console, no additional setup required
        logging.basicConfig(
            level=level, format='%(asctime)s %(levelname)s %(message)s')
    update_status = cfg.output == 's'
    list_status = cfg.output == 'd'

    log = cfg['log'] if 'log' in cfg else None
    test = cfg['test'] if 'test' in cfg else False
    skipped_test = 0

    unbox = cfg['unbox']
    from_into = "from" if unbox else "into"
    unbox_multi = cfg['unbox_multi']
    delete = cfg['delete']
    create_folders = cfg['create_folders']
    zip_structure = cfg['zip_structure']
    zip_archives = cfg['zip_archives']
    match_groups = cfg['match_groups']
    si = cfg['si']

    def globber(root, glob_expr):
        nonlocal skipped, regex
        if not isinstance(glob_expr, list):
            glob_expr = [glob_expr]
        for ge in glob_expr:
            for fn in Path(root).glob(ge):
                if regex and not regex.match(str(fn)):
                    info(f'Skipping {fn} as it does not match provided regex.')
                    skipped += 1
                    continue
                if (fn.is_file() and cfg['match_file']):
                    if not unbox and not zip_archives and fn.suffix in ARCHIVE_SUFFIXES:
                        info(f'Skipping {fn} as it is an archive and --zip_archives was not specified.')
                        skipped += 1
                        continue
                    if match_groups and (
                            (not unbox and fn.suffix in cfg['group_map']) or
                            (unbox and Path(fn.stem).suffix in cfg['group_map'])
                    ):
                        parent, stem, suffix, extra = (fn.parent, fn.stem, fn.suffix, '') \
                            if not unbox else (fn.parent, Path(fn.stem).stem, Path(fn.stem).suffix, fn.suffix)
                        matches = []
                        for suffixes in cfg['group_map'][suffix]:
                            matches = [
                                parent / f'{stem}{sf}{extra}'
                                for sf in suffixes
                                if (parent / f'{stem}{sf}{extra}').is_file()
                            ]
                            if matches:
                                break
                        for group_fn in matches:
                            yield group_fn.relative_to(root).parent, group_fn.name
                    yield fn.relative_to(root).parent, fn.name
                elif (fn.is_dir() and cfg['match_dir']):
                    yield fn.relative_to(root).parent, fn.name

    def start(py7za):
        nonlocal running, current, info_command
        if info_command:
            info(f'"{py7za.working_dir}": '+list2cmdline([py7za.executable_7za, *py7za.arguments]))
        current += 1
        running.append(py7za)

    async def print_status():
        nonlocal done, running, current, total, from_into
        while True:
            if total == 0:
                stdout.write(f'\x1b[2K\rStarting ... ')
            else:
                stdout.write(f'\x1b[2K\rProcessing: {current} / {total} '
                             f'[{nice_size(total_content_size, si)} {from_into} {nice_size(total_zip_size, si)}] ... '
                             f'{" ".join([f"{str(py7za.progress)}/100%" for py7za in running if py7za.progress])}')
            stdout.flush()
            if done:
                return
            await sleep(0.5)

    async def run_all():
        nonlocal total, done, total_content_size, total_zip_size, skipped, finished, test, skipped_test
        global aiop

        zippers = []

        root = Path(cfg.root).absolute()
        target = Path(cfg.target).absolute() if 'target' in cfg else root
        n = 0
        for sub_path, fn in globber(cfg.root, cfg.glob):
            if print_result and n % 100 == 0 and not test:
                stdout.write(f'\x1b[2K\rMatching [{n}] ... ')
            n += 1
            if create_folders and not test:
                (target / sub_path).mkdir(parents=True, exist_ok=True)
            if not unbox:
                target_path = target / sub_path / fn if create_folders else target / fn
                if zip_structure:
                    content = sub_path / fn
                    wd = str(root)
                else:
                    content = root / sub_path / fn
                    wd = '.'
                if not test:
                    zippers.append(
                        Py7za(f'a "{target_path}{cfg.suffix}" "{content}" {cli_options}',
                              on_start=start, working_dir=wd))
                else:
                    skipped_test += 1
                    print(f'TEST in "{wd}": 7za.exe a "{target_path}{cfg.suffix}" "{content}" {cli_options}')
            else:
                archive = root / sub_path / fn
                if not unbox_multi and (
                        (archive.suffix == '.zip' and len(ZipFile(archive).filelist) > 1) or
                        ((await Py7za.list_archive(str(archive), meta_data_only=True))[2] > 1)):
                    info(f'Skipping {archive} as it has multiple files and --unbox_multi was not specified.')
                    skipped += 1
                    continue
                target_path = target / sub_path if create_folders else target
                if not test:
                    zippers.append(Py7za(f'x "{archive}" "-o{target_path}" {cli_options}', start))
                else:
                    skipped_test += 1
                    print(f'TEST: 7za.exe x "{archive}" "-o{target_path}" {cli_options}')
        if print_result:
            stdout.write(f'\x1b[2K\rMatched {n} object(s), '
                         f'start processing in up to {aiop.size} parallel processes ...\n')
        total = len(zippers)
        async for py7za in aiop.arun_many(zippers):
            finished += 1
            if py7za.return_code > 0:
                error(f'Return code {py7za.return_code} from: {list2cmdline([py7za.executable_7za, *py7za.arguments])}'
                      f'\n{py7za.errors.decode()}')
                continue
            fn = py7za.arguments[1]
            pfn = Path(fn)
            if not pfn.is_file():
                error(f'Archive file {fn} not found.')
                continue
            if print_result or update_status or log:
                if pfn.suffix == '.zip':
                    total_content_size += (cs := sum([zip_info.file_size for zip_info in ZipFile(fn).filelist]))
                else:
                    total_content_size += (cs := (await Py7za.list_archive(fn, meta_data_only=True))[0])
                total_zip_size += (zs := stat(fn).st_size)
                if log:
                    with open(log, 'a') as lf:
                        lf.write(f'{datetime.strftime(datetime.now(timezone.utc).astimezone(), "%Y-%m-%d %H:%M:%S%z")},'
                                 f'{fn},{nice_size(cs, si)},{cs},{nice_size(zs, si)},{zs}\n')
                if print_result:
                    if list_status:
                        stdout.write(f'\x1b[2K\r'
                                     f'{datetime.strftime(datetime.now(), "%H:%M:%S")}  '
                                     f'{nice_size(cs, si)} {from_into} {nice_size(zs, si)} {fn}\n')
                        stdout.write(f'Total: {finished} / {total} '
                                     f'[{nice_size(total_content_size, si)} '
                                     f'{from_into} {nice_size(total_zip_size, si)}] ({current - finished} running)')
                    else:
                        stdout.write(f'{datetime.strftime(datetime.now(), "%H:%M:%S")}  '
                                     f'{nice_size(cs, si)} {from_into} {nice_size(zs, si)} {fn}\n')
                    stdout.flush()
            if unbox and delete:
                os_remove(py7za.arguments[1])
            running.remove(py7za)
        done = True

    if update_status:
        await gather(run_all(), print_status())
    else:
        await run_all()

    if cfg.output != 'q':
        if update_status or print_result:
            stdout.write('\x1b[2K\r')
        print(f'Completed processing {nice_size(total_content_size)} '
              f'of files {"from" if unbox else "into"} {total} archives, totaling {nice_size(total_zip_size)}.'
              f'\nTook {datetime.now()-start_time}. Skipped {skipped} files matching glob.')
        if test:
            print(f'TEST: would have started {"un" if unbox else ""}boxing {skipped_test} matches.')


def print_help():
    from ._version import __version__
    print(
        '\npy7za-box '+__version__+', command line utility\n'
        '\nPy7za-box ("pizza box") replaces a set of files with individual .zip files\n'
        'containing the originals, or does the reverse by "unboxing" the archives.\n'
        'Py7za uses 7za.exe, more information on the project page.\n'
        '\n'
        'Usage: `py7za-box <glob expression(s)> [options]`\n'
        '\n'
        '<glob expression(s)>      : Glob expression(s) like "**/*.csv". (required)\n'
        '                            Add quotes if your expression contains spaces.\n'
        'Options:\n'
        '-h/--help                 : This text.\n'
        '-d/--delete               : Remove the source after (un)boxing. [True]\n'
        '-cf/--create_folders      : Recreate folder structure in target path. [True]\n'
        '-l/--log <path>           : Log source, size, target, size as .csv. [None]\n'
        '-el/--error_log <path>    : Log warnings and error messages to file. [None]\n'
        '-gm/--group_match [bool]  : Group files with grouped suffixes. [True]\n'
        '-md/--match_dir [bool]    : Glob expression(s) should match dirs. [False]\n'
        '-mf/--match_file [bool]   : Glob expression(s) should match files. [True]\n'
        '-p/--parallel <n>         : #Parallel processes to run [0 = available cores]\n'
        '-r/--root <path>          : Path glob expression(s) are relative to. ["."]\n'
        '-re/--regex <expr>        : Regex path of globbed files must match. [None]\n'
        '-t/--target <path>        : Root path for output. ["" / in-place]\n'
        '-u/--unbox/--unzip        : Unzip instead of zip (glob to match archives).\n'
        '-um/--unbox_multi         : Whether to unzip multi-file archives. [False]\n'
        '                            (implies --unbox, which can be omitted)\n'
        '-o/--output [d/l/q/s/v]   : Default (a line per archive with status), list,\n'
        '                            quiet, status, or verbose output. Verbose prints\n'
        '                            each full 7za command and logs at info level.\n'
        '                            Note: d/l/v do not work for all archive types.\n'
        '-si                       : Whether to use SI units for file sizes. [False]\n'
        '--test                    : Test mode - no files are changed. [False]\n'
        '-w/overwrite [a/s/u/t]    : Used overwrite mode when unboxing. [s]\n'
        '                            a:all, s:skip, u:rename new, t:rename existing.\n'
        '-za/--zip_archives [bool] : Whether to zip matched archives (again). [False]\n'
        '-zs/--zip_structure [bool]: Root sub-folder structure is archived. [False]\n'
        '-7/--7za                  : CLI arguments passed to 7za after scripted ones.\n'
        '                            Add quotes if passing more than one argument.\n'
        '\n'
        'Examples:\n'
        '\n'
        'Zip all .csv files in C:/Data and put the archives in C:/Archive:\n'
        '   py7za-box *.csv --root C:/Data --target C:/Archive\n'
        'Unzip all .csv.zip from C:/Archive and sub-folders to C:/Data:\n'
        '   py7za-box **/*.csv.zip --unbox --root C:/Archive -t C:/Data\n'
        'Zip folders named `Photo*` individually using maximum compression:\n'
        '   py7za-box Photo* -r "C:/My Photos" -md -mf 0 -t C:/Archive -7 "-mx9"\n\n'
    )


CLI_DEFAULTS = {
    'parallel': '0',
    'delete': True,
    'create_folders': True,
    'match_groups': True,
    'match_dir': False,
    'match_file': True,
    'output': 'd',
    'overwrite': 's',
    'si': False,
    'root': '.',
    'test': False,
    'unbox': False,
    'unbox_multi': False,
    'verbose': False,
    'zip_structure': False,
    'zip_archives': False,
    '7za': ''
}


def cli_entry_point():
    global aiop

    # enable sufficient ansi support on Windows
    if os_name == 'nt':
        from ctypes import windll
        k = windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)

    cfg = Config.startup(defaults=CLI_DEFAULTS, no_compound_keys=True, aliases={
        'h': 'help', 'p': 'parallel', 'cf': 'create_folders', 'md': 'match_dir', 'mf': 'match_file', 'u': 'unbox',
        'unzip': 'unbox', 'r': 'root', 'zs': 'zip_structure', 't': 'target', 'v': 'verbose', '7': '7za', 'g': 'glob',
        'o': 'output', 'w': 'overwrite', 'za': 'zip_archives', 'um': 'unbox_multi', 'l': 'log', 'le': 'log_error',
        'unzip_multi': 'unbox_multi', 'error_log': 'log_error', 'el': 'log_error', 're': 'regex',
        'regular_expression': 'regex', 'mg': 'match_groups'
    })

    if cfg.get_as_type('help', bool, False):
        print_help()
        exit(0)

    if len(cfg.arguments['']) < 2 and 'glob' not in cfg:
        error('Missing required argument glob expression(s), e.g. `py7za-box *.csv [options]`.')
        print_help()
        exit(1)
    else:
        cfg.glob = cfg.glob if 'glob' in cfg else cfg.parameters

    if not Path(cfg.root).is_dir():
        error(f'The provided root directory "{cfg.root}" was not found.')
        exit(2)

    target = cfg.root if 'target' not in cfg or cfg.target is True else cfg.get_as_type('target', str)
    if not Path(target).is_dir():
        error(f'The provided target directory "{cfg.target}" was not found.')
        exit(2)

    if cfg.unbox and cfg.create_folders and 'target' in cfg and target is not True:
        warning(f'When unboxing to a target location (not in-place), original structure cannot be restored '
                f'unless sub-folder from root were included when the archives were created.')

    if cfg.zip_structure and cfg.unbox:
        warning(f'The --zip_structure option was specified, but does nothing when unboxing and will be ignored.')

    if cfg.zip_archives and cfg.unbox:
        warning(f'The --zip_archives option was specified, but does nothing when unboxing and will be ignored.')

    if cfg.unbox_multi and not cfg.unbox:
        if 'unbox' in cfg.arguments:
            warning(f'The --unbox_multi option was specified, but unbox was set to False, so the option is ignored.')
        else:
            # set unbox to true if only unbox_multi was provided
            cfg.unbox = True

    if cfg.zip_structure and cfg.create_folders:
        warning(f'Keeping sub-folders from root in archives, as well creating the folder structure in the '
                f'target location may produce unexpected results.')

    output_modes = {
        'd': 'd', 'default': 'd',
        'l': 'l', 'list': 'l',
        'q': 'q', 'quiet': 'q',
        's': 's', 'status': 's',
        'v': 'v', 'verbose': 'v'
    }
    if cfg.verbose:
        if 'output' in cfg.arguments:
            warning(f'Setting --verbose to True overrides any --output options with \'verbose\'.')
        cfg.output = 'v'
    if cfg.output not in output_modes:
        error(f'Unknown output mode {cfg.output}, provide default(d), list(l), quiet(q), status(s) or verbose(v).')
        print_help()
        exit(1)
    cfg.output = output_modes[cfg.output]

    overwrite_modes = {
        'a': 'a', 'all': 'a',
        's': 's', 'skip': 's',
        'u': 'u', 'rename_new': 'u',
        't': 't', 'rename_existing': 't'
    }
    if cfg.overwrite not in overwrite_modes:
        error(f'Unknown overwrite mode {cfg.output}, provide all(a), skip(s), rename_new(u) or rename_existing(t).')
        print_help()
        exit(1)
    cfg.overwrite = overwrite_modes[cfg.overwrite]
    if cfg.overwrite != 's' and not cfg.unbox:
        warning(f'Overwrite mode {cfg.overwrite} passed, but option will have no effect unless unboxing.')

    if cfg['match_groups']:
        groups_file = Path(__file__).parent / 'groups.json'
        if not groups_file.is_file():
            warning(f'Group matching specified, but no groups.json found in script installation directory.')
        else:
            try:
                with open(str(groups_file), 'r') as f:
                    groups = load(f)
            except (IOError, JSONDecodeError) as e:
                error(f'Error reading groups.json for group matching: {e}')
            cfg['group_map'] = {
                suffix: [
                    [other for other in g if other != suffix] for g in groups.values() if suffix in g
                ] for suffix in [s for v in groups.values() for s in v]
            }

    try:
        get_event_loop().run_until_complete(box(cfg))
    except KeyboardInterrupt:
        print('\nExecution interrupted, cleaning up...')


if __name__ == '__main__':
    cli_entry_point()
