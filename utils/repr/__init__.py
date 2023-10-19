import os

from colorama import init


if os.name == 'nt':
    from colorama import just_fix_windows_console

    just_fix_windows_console()

init()
