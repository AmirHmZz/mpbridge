import os
import subprocess
import tempfile
import time
from typing import Union
import sys

from watchdog.events import (
    FileSystemEventHandler,
    DirCreatedEvent,
    FileCreatedEvent,
    FileModifiedEvent,
    DirMovedEvent,
    FileMovedEvent, DirDeletedEvent, FileDeletedEvent, DirModifiedEvent)
from watchdog.observers import Observer


def open_dir(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


class Session:
    def list_all(self, path: str, files: list, folders: list):
        result = subprocess.run([
            "mpremote",
            "resume",
            "ls",
            path
        ], capture_output=True)
        for item in result.stdout.decode().split("\r\n")[1:-1]:
            if not item:
                continue
            size, filename = item.lstrip(" ").split(" ", maxsplit=1)
            if filename.endswith("/"):
                folders.append(path + filename)
                self.list_all(
                    path=path + filename, files=files, folders=folders)
            else:
                files.append(path + filename)

    def copy_all(self, dir_path):
        files = []
        folders = []
        self.list_all(path="/", files=files, folders=folders)
        for folder in folders:
            os.makedirs(dir_path + folder, exist_ok=True)
        for i, file in enumerate(files):
            result = subprocess.run([
                "mpremote",
                "resume",
                "cp",
                f":{file}",
                dir_path + file
            ], capture_output=True)
            print(f"{(i + 1) * 100 // len(files)}% Completed")
        print("Synced all contents successfully")

    def start_session(self):
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            self.copy_all(dir_path=tmp_dir_path)
            observer = Observer()
            observer.schedule(
                EventHandler(tmp_dir_path),
                tmp_dir_path, recursive=True)
            observer.start()
            open_dir(tmp_dir_path)
            print("Session opened successfully")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()


class EventHandler(FileSystemEventHandler):
    def dispatch(self, event):
        super().dispatch(event)
        time.sleep(0.2)

    def __init__(self, base_path) -> None:
        self.base_path = base_path.replace("\\", "/")

    @staticmethod
    def interpret_result(result: subprocess.CompletedProcess):
        if result.stderr:
            print("Operation failed:\n", result.stderr)
        elif b"Traceback (most recent call last)" in result.stdout:
            print("Operation failed:\n", result.stdout)
        else:
            print("Operation done successfully")

    def on_moved(self, event: Union[DirMovedEvent, FileMovedEvent]):
        src_path: str = event.src_path.replace("\\", "/").removeprefix(self.base_path)
        dest_path: str = event.dest_path.replace("\\", "/").removeprefix(self.base_path)
        result = subprocess.run([
            "mpremote",
            "resume",
            "exec",
            f'from os import rename; rename("{src_path}", "{dest_path}")'
        ], capture_output=True)
        super().on_moved(event)
        return self.interpret_result(result)

    def on_created(self, event: Union[DirCreatedEvent, FileCreatedEvent]):
        src_path: str = event.src_path.replace("\\", "/")
        if event.is_directory:
            result = subprocess.run([
                "mpremote",
                "resume",
                "mkdir",
                src_path.removeprefix(self.base_path)
            ], capture_output=True)
        else:
            result = subprocess.run([
                "mpremote",
                "resume",
                "cp",
                src_path,
                f":{src_path.removeprefix(self.base_path)}",
            ], capture_output=True)
        super().on_created(event)
        return self.interpret_result(result)

    def on_deleted(self, event: Union[DirDeletedEvent, FileDeletedEvent]):
        src_path: str = event.src_path.replace("\\", "/").removeprefix(self.base_path)
        result = subprocess.run([
            "mpremote",
            "resume",
            "rm",
            src_path
        ], capture_output=True)

        if b"[Errno 21] EISDIR" in result.stdout:
            result = subprocess.run([
                "mpremote",
                "resume",
                "rmdir",
                src_path
            ], capture_output=True)
        super().on_deleted(event)
        return self.interpret_result(result)

    def on_modified(self, event: Union[FileModifiedEvent, DirModifiedEvent]):
        src_path: str = event.src_path.replace("\\", "/")
        if not event.is_directory:
            result = subprocess.run([
                "mpremote",
                "resume",
                "cp",
                src_path,
                f":{src_path.removeprefix(self.base_path)}",
            ], capture_output=True)
            return self.interpret_result(result)


if __name__ == "__main__":
    Session().start_session()
