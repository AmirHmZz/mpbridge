import tempfile
import time

import click
from watchdog.observers import Observer

from src.handler import EventHandler
from src.pyboard import SweetPyboard
from src.utils import open_dir


@click.group()
def cli():
    pass


@cli.command()
@click.argument('port')
def start(port):
    pyb = SweetPyboard(device=port)
    pyb.enter_raw_repl()

    with tempfile.TemporaryDirectory() as tmp_dir_path:
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


if __name__ == '__main__':
    cli()
