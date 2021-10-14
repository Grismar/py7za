import shlex
from typing import Union, List
from pathlib import Path
from asyncio import create_subprocess_exec, run
from asyncio.subprocess import PIPE
from shutil import which
from os import name as os_name


class Py7za:
    """
    Wrapper class for running 7za.exe.

    Attributes
    ----------
    executable_7za: str (class)
        full file path to 7za.exe, executable from calling script working directory (or just '7za' on non-Windows)
    progress: int
        7za operation progress
    files: List[str]
        files that were processed in the operation
    done: bool
        whether operation has completed
    errors: bytes
        stderr of operation, once it completes (or fails)
    """
    executable_7za = str(Path(__file__).parent / '../bin/7za.exe') if os_name == 'nt' else '7za'

    def __init__(self, arguments: Union[str, List[str]]):
        if which(self.executable_7za) is None:
            raise FileNotFoundError(f'7za executable "{self.executable_7za}" not found.')

        if isinstance(arguments, str):
            arguments = shlex.split(arguments, posix=False)

        # ignore output arguments passed, always pass progress and output to 1, disable log
        self.arguments = [a for a in arguments if a[:3] not in ['-bs', '-bb']] + ['-bsp1', '-bso1', '-bb']

        self.progress = 0
        self.files = []

        self.done = False
        self.errors = None
        self.return_code = None

    def __await__(self):
        return self.arun().__await__()

    def _parse_stdout(self, line):
        if line:
            line = line.decode()
            if line[0] in '+U':
                self.files.append((line[0], line[2:]))
            if len(line) >= 4 and line[3] == '%':
                self.progress = int(line[:3].strip())

    async def arun(self) -> 'Py7za':
        """
        Run 7za asynchronously, updating .progress and .files during the run and .done and errors when it completes
        :return: return code of process
        """
        self.progress = 0
        self.files = []

        self.done = False
        self.errors = None

        proc = await create_subprocess_exec(self.executable_7za, *self.arguments, stdout=PIPE, stderr=PIPE)

        line = b''
        while True:
            b = await proc.stdout.read(1)
            if b == b'\r':
                self._parse_stdout(line)
                line = b''
            else:
                line += b
            # stdout read will return b'' when the process has ended
            if b == b'':
                self.errors = await proc.stderr.read()
                await proc.wait()
                self.done = True
                if proc.returncode == 0:
                    self.progress = 100
                self.return_code = proc.returncode
                return self

    def run(self) -> int:
        """
        Run and await arun()
        :return: return code of process
        """
        return run(self.arun())
