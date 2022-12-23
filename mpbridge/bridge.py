import tempfile
import time

from watchdog.observers import Observer

from .handler import EventHandler
from .pyboard import SweetPyboard
from .utils import open_dir


def start(port):
    pyb = SweetPyboard(device=port)
    pyb.enter_raw_repl()

    with tempfile.TemporaryDirectory(prefix="mpbridge-") as tmp_dir_path:
        pyb.copy_all(dest_dir_path=tmp_dir_path)
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
        observer.join()
