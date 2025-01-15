import os
import pathlib
import shutil
import subprocess
import tempfile
import time
from argparse import Namespace
from typing import Optional

import serial.tools.list_ports
from colorama import Fore
from mpremote.main import State, argparse_repl
from watchdog.observers import Observer

from . import utils
from .handler import EventHandler
from .ignore import IgnoreStorage
from .serial_transport import ExtendedSerialTransport


def start_bridge_mode(port: str):
    port = utils.port_abbreviation(port)
    print(Fore.YELLOW, "- Starting bridge mode on", port)
    utils.reset_term_color()
    st = ExtendedSerialTransport(device=port)
    st.enter_raw_repl_verbose()

    with tempfile.TemporaryDirectory(
        prefix=utils.get_temp_dirname_prefix(port)
    ) as tmp_dir_path:
        st.copy_all(dest_dir_path=tmp_dir_path)
        print(Fore.YELLOW, "- Started bridge mode in", tmp_dir_path)
        print(Fore.YELLOW, "- Use Ctrl-C to terminate the bridge")
        utils.reset_term_color()
        observer = Observer()
        observer.schedule(
            EventHandler(st=st, base_path=tmp_dir_path), tmp_dir_path, recursive=True
        )
        observer.start()
        utils.open_dir(tmp_dir_path)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            st.exit_raw_repl_verbose()
        observer.join()


def sync(
    port: str,
    path: str,
    clean: bool,
    dry_run: bool,
    push_only: bool,
    use_hashtable: bool,
):
    port = utils.port_abbreviation(port)
    print(Fore.YELLOW, f"- Syncing files on {port} with {path}")
    utils.reset_term_color()
    st = ExtendedSerialTransport(device=port)
    st.enter_raw_repl_verbose()
    if clean:
        print(Fore.YELLOW, f"Removing absent files from {port}")
        st.delete_absent_items(dir_path=path, dry=dry_run)
    st.sync_with_dir(
        dir_path=path, dry=dry_run, push=push_only, use_hashtable=use_hashtable
    )
    st.exit_raw_repl_verbose()


def start_dev_mode(
    port: str,
    path: str,
    auto_reset: str,
    no_prompt: bool,
    use_hashtable: bool,
    mpy_cross_path: Optional[str],
):
    path = utils.replace_backslashes(path)
    port = utils.port_abbreviation(port)
    print(Fore.YELLOW, f"- Syncing files on {port} with {path}")
    utils.reset_term_color()

    while True:
        if mpy_cross_path is None:
            _dev_mode_iter(
                port=port,
                path=path,
                auto_reset=auto_reset,
                no_prompt=no_prompt,
                use_hashtable=use_hashtable,
            )

        else:
            with tempfile.TemporaryDirectory(
                prefix=utils.get_temp_dirname_prefix(port)
            ) as tmp_dir_path:
                ignore = IgnoreStorage(dir_path=path)
                ldirs, lfiles = utils.recursive_list_dir(path)

                for ldir in ldirs.keys():
                    os.mkdir(tmp_dir_path + ldir)
                for lfile_rel, lfile_abs in lfiles.items():
                    if not ignore.match_file(lfile_rel):
                        if lfile_rel != "/main.py" and lfile_rel.endswith(".py"):
                            subprocess.run(
                                [
                                    mpy_cross_path,
                                    "-o",
                                    tmp_dir_path + lfile_rel[:-3] + ".mpy",
                                    lfile_abs,
                                ],
                                capture_output=False,
                            )
                        else:
                            shutil.copyfile(src=lfile_abs, dst=tmp_dir_path + lfile_rel)
                _dev_mode_iter(
                    port=port,
                    path=tmp_dir_path,
                    auto_reset=auto_reset,
                    no_prompt=no_prompt,
                    use_hashtable=use_hashtable,
                )


def _dev_mode_iter(
    port: str,
    path: str,
    auto_reset: str,
    no_prompt: bool,
    use_hashtable: bool,
):
    st = ExtendedSerialTransport(device=port)
    st.enter_raw_repl_verbose()
    if not no_prompt:
        print(Fore.YELLOW, "- Sync files")
        st.sync_with_dir(dir_path=path, use_hashtable=use_hashtable)
        print(
            Fore.LIGHTWHITE_EX
            + " ? Press [Enter] to Clean Sync & Enter REPL\n"
            + "   Press [Ctrl + C] to exit ",
            end="",
        )
        utils.reset_term_color()
        input()
    print(Fore.YELLOW, "- Clean Sync files")
    st.delete_absent_items(dir_path=path)
    st.sync_with_dir(dir_path=path, use_hashtable=use_hashtable)
    if auto_reset is None:
        st.exit_raw_repl()
        st.close()
    elif auto_reset == "hard":
        st.verbose_hard_reset()
        st.close()
        time.sleep(1)
    elif auto_reset == "soft":
        st.exit_raw_repl()
        st.verbose_soft_reset()
        st.close()
    start_repl(port)


def clear(port: str):
    port = utils.port_abbreviation(port)
    st = ExtendedSerialTransport(device=port)
    st.enter_raw_repl_verbose()
    st.clear_all()
    st.exit_raw_repl_verbose()


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


def list_devices():
    ports = sorted(serial.tools.list_ports.comports())
    if ports:
        for i, port in enumerate(ports):
            print(
                Fore.LIGHTYELLOW_EX,
                "{}. {} {} {:04x}:{:04x} {} {}".format(
                    i + 1,
                    port.device,
                    port.serial_number or "null",
                    port.vid if isinstance(port.vid, int) else 0,
                    port.pid if isinstance(port.pid, int) else 0,
                    port.manufacturer or "null",
                    port.product or "null",
                ),
            )
    else:
        print(Fore.LIGHTYELLOW_EX, "Couldn't find any connected devices")
    utils.reset_term_color()
