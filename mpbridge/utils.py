import os
import re
import subprocess
import sys

from colorama import Style


def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


def replace_backslashes(path: str) -> str:
    return path.replace("\\", "/")


def open_dir(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def print_progress_bar(
        iteration,
        total,
        prefix='',
        suffix='',
        decimals=1,
        length=100,
        fill='█',
        print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()


def reset_term_color():
    print(Style.RESET_ALL, end="")


def port_abbreviation(port: str):
    if re.fullmatch(r"^[auc]\d{1,2}$", port):
        if port[0] == "c":
            port = "COM" + port[1:]
        elif port[0] == "a":
            port = "/dev/ttyACM" + port[1:]
        elif port[0] == "u":
            port = "/dev/ttyUSB" + port[1:]
    return port
