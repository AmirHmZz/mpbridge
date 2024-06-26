import itertools
import os
from contextlib import suppress

from colorama import Fore
from mpremote.transport_serial import SerialTransport, TransportError

from . import utils
from .ignore import IgnoreStorage
from .utils import unpack_length_prefixed

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
            yield idir, False, 0
for item in iter_dir("/"):
    print(item, end=",")
"""

SHA1_FUNC = """
from hashlib import sha1
from gc import collect
b = bytearray(1024)
mv = memoryview(b)
def get_sha1(path):
    h = sha1()
    with open(path,"rb") as f:
        while s := f.readinto(b):
            h.update(mv[:s])
    collect()
    return h.digest()
"""


def generate_buffer():
    buf = bytearray()

    def repr_consumer(b):
        nonlocal buf
        buf.extend(b.replace(b"\x04", b""))

    return buf, repr_consumer


class ExtendedSerialTransport(SerialTransport):
    def fs_recursive_listdir(self):
        buf, consumer = generate_buffer()
        self.exec(RECURSIVE_LS, data_consumer=consumer)
        dirs = {}
        files = {}
        for item in eval(f'[{buf.decode("utf-8")}]'):
            if item[1]:
                files[item[0]] = item[2]
            else:
                dirs[item[0]] = item[2]
        return dirs, files

    def fs_verbose_get(self, src, dest, chunk_size=1024, dry: bool = False):
        def print_prog(written, total):
            utils.print_progress_bar(
                iteration=written, total=total, decimals=0,
                prefix=f"{Fore.LIGHTCYAN_EX} ↓ Getting {src}".ljust(60),
                suffix="Complete", length=15)

        if not dry:
            self.fs_get(src, dest, chunk_size=chunk_size, progress_callback=print_prog)
        print_prog(1, 1)
        utils.reset_term_color(new_line=True)

    def fs_verbose_put(self, src, dest, chunk_size=1024, dry: bool = False):
        def print_prog(written, total):
            utils.print_progress_bar(
                iteration=written, total=total, decimals=0,
                prefix=f"{Fore.LIGHTYELLOW_EX} ↑ Putting {dest}".ljust(60),
                suffix="Complete", length=15)

        if not dry:
            self.fs_put(src, dest, chunk_size=chunk_size, progress_callback=print_prog)
        print_prog(1, 1)
        utils.reset_term_color(new_line=True)

    def fs_verbose_rename(self, src, dest, dry: bool = False):
        if not dry:
            buf, consumer = generate_buffer()
            self.exec(f'from os import rename; rename("{src}", "{dest}")',
                      data_consumer=consumer)
        print(Fore.LIGHTBLUE_EX, "O Rename", src, "→", dest)
        utils.reset_term_color()

    def fs_verbose_mkdir(self, dir_path, dry: bool = False):
        if not dry:
            self.fs_mkdir(dir_path)
        print(Fore.LIGHTGREEN_EX, "* Created", dir_path)
        utils.reset_term_color()

    def fs_verbose_rm(self, src, dry: bool = False):
        if not dry:
            self.fs_rm(src)
        print(Fore.LIGHTRED_EX, "✕ Removed", src)
        utils.reset_term_color()

    def fs_verbose_rmdir(self, dir_path, dry: bool = False):
        try:
            if not dry:
                self.fs_rmdir(dir_path)
        except TransportError:
            print(Fore.RED, "E Cannot remove directory", dir_path, "as it might be mounted")
        else:
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

    def sync_with_dir(self, dir_path, dry: bool = False, push: bool = False):
        print(Fore.YELLOW, "- Syncing")
        self.exec_raw_no_follow(SHA1_FUNC)
        dir_path = utils.replace_backslashes(dir_path)
        rdirs, rfiles = self.fs_recursive_listdir()
        ldirs, lfiles = utils.recursive_list_dir(dir_path)
        hashtable = self._get_hash_table()
        ignore = IgnoreStorage(dir_path=dir_path)
        if (not dry) and (not push):
            for rdir in rdirs.keys():
                if rdir not in ldirs and not ignore.match_dir(rdir):
                    os.makedirs(dir_path + rdir, exist_ok=True)
        for ldir in ldirs.keys():
            if ldir not in rdirs and not ignore.match_dir(ldir):
                self.fs_verbose_mkdir(ldir, dry=dry)
        for lfile_rel, lfiles_abs in lfiles.items():
            if ignore.match_file(lfile_rel):
                continue
            if rfiles.get(lfile_rel, None) == os.path.getsize(lfiles_abs):
                if lfile_rel in hashtable:
                    sha1 = hashtable[lfile_rel]
                else:
                    sha1 = self.get_sha1(lfile_rel)
                    hashtable[lfile_rel] = sha1
                if sha1 == utils.get_file_sha1(lfiles_abs):
                    continue
            hashtable[lfile_rel] = utils.get_file_sha1(lfiles_abs)
            self.fs_verbose_put(lfiles_abs, lfile_rel, chunk_size=256, dry=dry)
        if not push:
            for rfile, rsize in rfiles.items():
                if ignore.match_file(rfile):
                    continue
                if rfile not in lfiles:
                    self.fs_verbose_get(rfile, dir_path + rfile, chunk_size=256, dry=dry)
        self._write_hash_table(hashtable)
        print(Fore.LIGHTGREEN_EX, "✓ Files synced successfully")

    def delete_absent_items(self, dir_path, dry: bool = False):
        dir_path = utils.replace_backslashes(dir_path)
        rdirs, rfiles = self.fs_recursive_listdir()
        ldirs, lfiles = utils.recursive_list_dir(dir_path)
        ignore = IgnoreStorage(dir_path=dir_path)
        for rfile, rsize in rfiles.items():
            if not ignore.match_file(rfile) and rfile not in lfiles:
                self.fs_verbose_rm(rfile, dry=dry)
        for rdir in rdirs.keys():
            if not ignore.match_dir(rdir) and rdir not in ldirs:
                # There might be ignored files in folders
                with suppress(Exception):
                    self.fs_verbose_rmdir(rdir, dry=dry)

    def clear_all(self):
        print(Fore.YELLOW, "- Deleting all files from MicroPython board")
        rdirs, rfiles = self.fs_recursive_listdir()
        for rfile in rfiles.keys():
            self.fs_verbose_rm(rfile)
        for rdir in rdirs.keys():
            self.fs_verbose_rmdir(rdir)
        print(Fore.LIGHTGREEN_EX, "✓ Deleted all files from MicroPython board")

    def enter_raw_repl_verbose(self, soft_reset=True):
        print(Fore.YELLOW, "- Entering raw repl")
        utils.reset_term_color()
        return self.enter_raw_repl(soft_reset)

    def exit_raw_repl_verbose(self):
        print(Fore.YELLOW, "- Exiting raw repl")
        utils.reset_term_color()
        self.exit_raw_repl()

    def get_sha1(self, file_path):
        return eval(self.eval(
            f'get_sha1("{file_path}")').decode("utf-8"))

    def verbose_hard_reset(self):
        self.exec_raw_no_follow("from machine import reset; reset()")
        self.serial.close()
        print(Fore.LIGHTGREEN_EX, "✓ Hard reset board successfully")
        utils.reset_term_color()

    def verbose_soft_reset(self):
        self.serial.write(b"\x04")
        print(Fore.LIGHTGREEN_EX, "✓ Soft reset board successfully")

    def _get_hash_table(self) -> dict:
        with suppress(Exception):
            return dict(map(
                lambda t: (t[0].decode("utf-8"), t[1]),
                itertools.batched(
                    unpack_length_prefixed(
                        "B", self.fs_readfile("mpbridge.hashtable")), 2)))
        return {}

    def _write_hash_table(self, hash_table: dict[str, bytes]):
        # TODO Ignore update if not changed
        self.fs_writefile(
            "mpbridge.hashtable",
            b"".join(map(
                lambda i: len(i[0]).to_bytes() + i[0].encode("utf-8") + len(i[1]).to_bytes() + i[1],
                hash_table.items())))
        print(Fore.LIGHTGREEN_EX, "✓ Updated hashtable")
