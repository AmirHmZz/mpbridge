import os

from colorama import Fore
from mpremote.pyboard import Pyboard

from .utils import print_progress_bar, reset_term_color

RECURSIVE_LS = """
from os import ilistdir
from gc import collect
def iter_dir(dir_path):
    collect()
    for item in ilistdir(dir_path):
        if dir_path[-1] != "/":
            dir_path += "/"
        idir = f"{dir_path}{item[0]}"
        if item[1] == 0x8000:
            yield idir, True
        else:
            yield from iter_dir(idir)
            yield idir, False
for item in iter_dir("/"):
    print(item, end=",")
"""


def generate_buffer():
    buf = bytearray()

    def repr_consumer(b):
        nonlocal buf
        buf.extend(b.replace(b"\x04", b""))

    return buf, repr_consumer


class SweetPyboard(Pyboard):
    def fs_recursive_listdir(self):
        buf, consumer = generate_buffer()
        self.exec_(RECURSIVE_LS, data_consumer=consumer)
        return eval(f'[{buf.decode("utf-8")}]')

    def fs_verbose_get(self, src, dest, chunk_size=1024):
        def print_prog(written, total):
            print_progress_bar(
                iteration=written, total=total, decimals=0,
                prefix=f"{Fore.LIGHTCYAN_EX} ↓ Getting {src}\t\t",
                suffix="Complete", length=20)

        self.fs_get(src, dest, chunk_size=chunk_size, progress_callback=print_prog)
        reset_term_color()

    def fs_verbose_put(self, src, dest, chunk_size=1024):
        def print_prog(written, total):
            print_progress_bar(
                iteration=written, total=total, decimals=0,
                prefix=f"{Fore.LIGHTYELLOW_EX} ↑ Putting {dest}\t\t",
                suffix="Complete", length=20)

        self.fs_put(src, dest, chunk_size=chunk_size, progress_callback=print_prog)
        reset_term_color()

    def fs_verbose_rename(self, src, dest):
        buf, consumer = generate_buffer()
        self.exec_(f'from os import rename; rename("{src}", "{dest}")',
                   data_consumer=consumer)
        print(Fore.LIGHTBLUE_EX, "O Rename", src, "→", dest)
        reset_term_color()

    def fs_verbose_mkdir(self, dir_path):
        self.fs_mkdir(dir_path)
        print(Fore.LIGHTGREEN_EX, "* Created", dir_path)
        reset_term_color()

    def fs_verbose_rm(self, src):
        self.fs_rm(src)
        print(Fore.LIGHTRED_EX, "✕ Removed", src)
        reset_term_color()

    def fs_verbose_rmdir(self, dir_path):
        self.fs_rmdir(dir_path)
        print(Fore.LIGHTRED_EX, "✕ Removed", dir_path)
        reset_term_color()

    def copy_all(self, dest_dir_path):
        fs_records = self.fs_recursive_listdir()
        for item in filter(lambda rec: not rec[1], fs_records):
            os.makedirs(dest_dir_path + item[0], exist_ok=True)
        for item in filter(lambda rec: rec[1], fs_records):
            self.fs_verbose_get(item[0], dest_dir_path + item[0], chunk_size=256)
        print(Fore.LIGHTGREEN_EX, "✓ Copied all files successfully")
        reset_term_color()
