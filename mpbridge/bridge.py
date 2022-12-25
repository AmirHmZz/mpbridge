import tempfile
import time

from colorama import Fore
from watchdog.observers import Observer

from .handler import EventHandler
from .pyboard import SweetPyboard
from .utils import open_dir, port_abbreviation, remove_prefix, reset_term_color


def _get_temp_dir_name(full_port: str):
    return "mpbridge-" + remove_prefix(
        full_port, "/dev/").replace(
        "tty", "").replace(
        "/", "-") + "-"


def start(port):
    port = port_abbreviation(port)
    print(Fore.YELLOW, "- Starting filesystem bridge on", port)
    reset_term_color()
    pyb = SweetPyboard(device=port)
    pyb.enter_raw_repl_verbose()

    with tempfile.TemporaryDirectory(prefix=_get_temp_dir_name(port)) as tmp_dir_path:
        pyb.copy_all(dest_dir_path=tmp_dir_path)
        print(Fore.YELLOW, "- Started filesystem bridge in", tmp_dir_path)
        print(Fore.YELLOW, "- Use Ctrl-C to terminate the bridge")
        reset_term_color()
        observer = Observer()
        observer.schedule(
            EventHandler(pyb=pyb, base_path=tmp_dir_path),
            tmp_dir_path, recursive=True)
        observer.start()
        open_dir(tmp_dir_path)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            pyb.exit_raw_repl_verbose()
        observer.join()
