import tempfile
import time

from colorama import Fore
from watchdog.observers import Observer

from .handler import EventHandler
from .pyboard import SweetPyboard
from . import utils


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


def sync(port: str, path: str):
    port = utils.port_abbreviation(port)
    print(Fore.YELLOW, f"- Syncing files on {port} with {path}")
    utils.reset_term_color()
    pyb = SweetPyboard(device=port)
    pyb.enter_raw_repl_verbose()
    pyb.sync_with_dir(dir_path=path)
    pyb.exit_raw_repl_verbose()
