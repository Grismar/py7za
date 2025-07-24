from os import name as os_name
from sys import stdout

ANSI_ENABLED = True


def aprint(s: str = '', cr: bool = True):
    if ANSI_ENABLED:
        if cr:
            stdout.write('\x1b[2K\r')
        stdout.write(s)
    else:
        print(s if not s or s[-1] != '\n' else s[:-1])


def ansi_enabled(value: bool = True) -> bool:
    global ANSI_ENABLED
    ANSI_ENABLED = value
    # enable sufficient ansi support on Windows
    if os_name == 'nt':
        from ctypes import windll, byref, c_int

        std_output_handle = -11
        enable_virtual_terminal_processing = 0x0004

        handle = windll.kernel32.GetStdHandle(std_output_handle)

        mode = c_int()
        if windll.kernel32.GetConsoleMode(handle, byref(mode)):
            new_mode = mode.value | enable_virtual_terminal_processing
            if not windll.kernel32.SetConsoleMode(handle, new_mode):
                return False
    return True
