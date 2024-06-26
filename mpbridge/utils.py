from __future__ import annotations

import hashlib
import os
import re
import struct
import subprocess
import sys

from colorama import Style


def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


def remove_suffix(string: str, suffix: str) -> str:
    if string.endswith(suffix):
        return string[:-len(suffix)]
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


def reset_term_color(new_line: bool = False):
    print(Style.RESET_ALL, end="\n" if new_line else "")


def port_abbreviation(port: str):
    if re.fullmatch(r"^[auc]\d{1,2}$", port):
        if port[0] == "c":
            port = "COM" + port[1:]
        elif port[0] == "a":
            port = "/dev/ttyACM" + port[1:]
        elif port[0] == "u":
            port = "/dev/ttyUSB" + port[1:]
    return port


def removeprefix(string, prefix):
    if not (isinstance(string, str) and isinstance(prefix, str)):
        raise TypeError('Param value type error')
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


def recursive_list_dir(path: str) -> tuple[dict[str, str], dict[str, str]]:
    out_dirs = {}
    out_files = {}
    for abs_dir, dirs, files in os.walk(replace_backslashes(path), followlinks=True):
        abs_dir = replace_backslashes(abs_dir)
        rel_dir = removeprefix(abs_dir, path)
        for dir_name in dirs:
            out_dirs[f"{rel_dir}/{dir_name}"] = f"{abs_dir}/{dir_name}"
        for file_name in files:
            out_files[f"{rel_dir}/{file_name}"] = f"{abs_dir}/{file_name}"
    return out_dirs, out_files


def get_file_sha1(path: str) -> bytes:
    with open(path, "rb") as file:
        return hashlib.sha1(file.read()).digest()


def get_temp_dirname_prefix(full_port: str):
    return "mpbridge-" + remove_prefix(
        full_port, "/dev/").replace(
        "tty", "").replace(
        "/", "-") + "-"


def unpack_length_prefixed(
        size_header_fmt: str,
        data: bytes | bytearray | memoryview):
    size_header_size = struct.calcsize(size_header_fmt)

    i = 0
    while i < len(data):
        size = struct.unpack(size_header_fmt, data[i:i + size_header_size])[0]
        i += size_header_size

        yield data[i: i + size]
        i += size
