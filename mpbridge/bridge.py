import tempfile
import time
from argparse import Namespace

from colorama import Fore
from mpremote.main import State, argparse_repl
from watchdog.observers import Observer

from . import utils
from .handler import EventHandler
from .pyboard import SweetPyboard


def start_bridge_mode(port: str):
    port = utils.port_abbreviation(port)
    print(Fore.YELLOW, "- Starting bridge mode on", port)
    utils.reset_term_color()
    pyb = SweetPyboard(device=port)
    pyb.enter_raw_repl_verbose()

    with tempfile.TemporaryDirectory(
            prefix=utils.get_temp_dirname_prefix(port)) as tmp_dir_path:
        pyb.copy_all(dest_dir_path=tmp_dir_path)
        print(Fore.YELLOW, "- Started bridge mode in", tmp_dir_path)
        print(Fore.YELLOW, "- Use Ctrl-C to terminate the bridge")
        utils.reset_term_color()
        observer = Observer()
        observer.schedule(
            EventHandler(pyb=pyb, base_path=tmp_dir_path),
            tmp_dir_path, recursive=True)
        observer.start()
        utils.open_dir(tmp_dir_path)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            pyb.exit_raw_repl_verbose()
        observer.join()


def sync(port: str, path: str, clean: bool):
    port = utils.port_abbreviation(port)
    print(Fore.YELLOW, f"- Syncing files on {port} with {path}")
    utils.reset_term_color()
    pyb = SweetPyboard(device=port)
    pyb.enter_raw_repl_verbose()
    if clean:
        pyb.delete_absent_items(dir_path=path)
    pyb.sync_with_dir(dir_path=path)
    pyb.exit_raw_repl_verbose()


def start_dev_mode(port: str, path: str, auto_reset: str):
    path = utils.replace_backslashes(path)
    port = utils.port_abbreviation(port)
    print(Fore.YELLOW, f"- Syncing files on {port} with {path}")
    utils.reset_term_color()

    while True:
        pyb = SweetPyboard(device=port)
        pyb.enter_raw_repl_verbose()
        pyb.sync_with_dir(dir_path=path)
        old_ls = utils.recursive_list_dir(path)
        print(Fore.LIGHTWHITE_EX +
              " ? Press [Enter] to Sync & Enter REPL\n" +
              "   Press [Ctrl + C] to exit ", end="")
        utils.reset_term_color()
        input()
        push_deletes(pyb, path, old_ls=old_ls)
        pyb.sync_with_dir(dir_path=path)
        if auto_reset is None:
            pyb.exit_raw_repl()
            pyb.close()
        elif auto_reset == "hard":
            pyb.verbose_hard_reset()
            pyb.close()
            time.sleep(1)
        elif auto_reset == "soft":
            pyb.exit_raw_repl()
            pyb.verbose_soft_reset()
            pyb.close()
        start_repl(port)


def clear(port: str):
    port = utils.port_abbreviation(port)
    pyb = SweetPyboard(device=port)
    pyb.enter_raw_repl_verbose()
    pyb.clear_all()
    pyb.exit_raw_repl_verbose()


def start_repl(port: str):
    from mpremote.commands import do_connect, do_disconnect
    from mpremote.repl import do_repl
    print(Fore.LIGHTMAGENTA_EX, "R Entering REPL using mpremote")
    utils.reset_term_color()
    port = utils.port_abbreviation(port)
    state = State()
    do_connect(state, Namespace(device=[port], next_command=[]))
    do_repl(state, argparse_repl().parse_args([]))
    do_disconnect(state)
    print("\n" + Fore.LIGHTMAGENTA_EX, "R Exiting REPL")
    utils.reset_term_color()


def push_deletes(pyb, path, old_ls: tuple):
    new_ls = utils.recursive_list_dir(path)
    for file in set(old_ls[1]).difference(new_ls[1]):
        pyb.fs_verbose_rm(file)
    for ddir in sorted(set(new_ls[0]).difference(new_ls[0]), reverse=True):
        pyb.fs_verbose_rmdir(ddir)
