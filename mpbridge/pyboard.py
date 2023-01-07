import os

from colorama import Fore
from mpremote.pyboard import Pyboard

from . import utils

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
            yield idir, True, item[3]
        else:
            yield from iter_dir(idir)
            yield idir, False, item[3]
for item in iter_dir("/"):
    print(item, end=",")
"""

GET_SHA1 = """
from hashlib import sha1
h = sha1()
b = bytearray(255)
mv = memoryview(b)
with open("{}","rb") as f:
    while s := f.readinto(b):
        h.update(mv[:s])
print(h.digest())
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
        dirs = {}
        files = {}
        for item in eval(f'[{buf.decode("utf-8")}]'):
            if item[1]:
                files[item[0]] = item[2]
            else:
                dirs[item[0]] = item[2]
        return dirs, files

    def fs_verbose_get(self, src, dest, chunk_size=1024):
        def print_prog(written, total):
            utils.print_progress_bar(
                iteration=written, total=total, decimals=0,
                prefix=f"{Fore.LIGHTCYAN_EX} ↓ Getting {src}\t\t",
                suffix="Complete", length=20)

        self.fs_get(src, dest, chunk_size=chunk_size, progress_callback=print_prog)
        print_prog(1, 1)
        utils.reset_term_color(new_line=True)

    def fs_verbose_put(self, src, dest, chunk_size=1024):
        def print_prog(written, total):
            utils.print_progress_bar(
                iteration=written, total=total, decimals=0,
                prefix=f"{Fore.LIGHTYELLOW_EX} ↑ Putting {dest}\t\t",
                suffix="Complete", length=20)

        self.fs_put(src, dest, chunk_size=chunk_size, progress_callback=print_prog)
        print_prog(1, 1)
        utils.reset_term_color(new_line=True)

    def fs_verbose_rename(self, src, dest):
        buf, consumer = generate_buffer()
        self.exec_(f'from os import rename; rename("{src}", "{dest}")',
                   data_consumer=consumer)
        print(Fore.LIGHTBLUE_EX, "O Rename", src, "→", dest)
        utils.reset_term_color()

    def fs_verbose_mkdir(self, dir_path):
        self.fs_mkdir(dir_path)
        print(Fore.LIGHTGREEN_EX, "* Created", dir_path)
        utils.reset_term_color()

    def fs_verbose_rm(self, src):
        self.fs_rm(src)
        print(Fore.LIGHTRED_EX, "✕ Removed", src)
        utils.reset_term_color()

    def fs_verbose_rmdir(self, dir_path):
        self.fs_rmdir(dir_path)
        print(Fore.LIGHTRED_EX, "✕ Removed", dir_path)
        utils.reset_term_color()

    def copy_all(self, dest_dir_path):
        rdirs, rfiles = self.fs_recursive_listdir()
        for rdir in rdirs:
            os.makedirs(dest_dir_path + rdir, exist_ok=True)
        for rfile in rfiles:
            self.fs_verbose_get(rfile, dest_dir_path + rfile, chunk_size=256)
        print(Fore.LIGHTGREEN_EX, "✓ Copied all files successfully")
        utils.reset_term_color()

    def sync_with_dir(self, dir_path):
        dir_path = utils.replace_backslashes(dir_path)
        rdirs, rfiles = self.fs_recursive_listdir()
        ldirs, lfiles = utils.recursive_list_dir(dir_path)
        for rdir in rdirs.keys():
            if rdir not in ldirs:
                os.makedirs(dir_path + rdir, exist_ok=True)
        for ldir in ldirs.keys():
            if ldir not in rdirs:
                self.fs_verbose_mkdir(ldir)
        for lfile_rel, lfiles_abs in lfiles.items():
            if rfiles.get(lfile_rel, None) == os.path.getsize(lfiles_abs):
                if self.get_sha1(lfile_rel) == utils.get_file_sha1(lfiles_abs):
                    continue
            self.fs_verbose_put(lfiles_abs, lfile_rel, chunk_size=256)
        print(Fore.LIGHTGREEN_EX, "✓ Synced files successfully")

        for rfile, rsize in rfiles.items():
            if rfile not in lfiles:
                self.fs_verbose_get(rfile, dir_path + rfile, chunk_size=256)

    def enter_raw_repl_verbose(self, soft_reset=True):
        print(Fore.YELLOW, "- Entering raw repl")
        utils.reset_term_color()
        return self.enter_raw_repl(soft_reset)

    def exit_raw_repl_verbose(self):
        print(Fore.YELLOW, "- Exiting raw repl")
        utils.reset_term_color()
        self.exit_raw_repl()

    def get_sha1(self, file_path):
        buf, consumer = generate_buffer()
        self.exec_(GET_SHA1.format(file_path), data_consumer=consumer)
        return eval(buf.decode("utf-8"))
