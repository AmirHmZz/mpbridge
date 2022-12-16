import os
import subprocess
import sys


def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix):]
    return prefix


def replace_backslashes(path: str) -> str:
    return path.replace("\\", "/")


def open_dir(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])
