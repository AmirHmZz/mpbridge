import subprocess
import time
from typing import Union

from watchdog.events import (
    FileSystemEventHandler,
    DirCreatedEvent,
    FileCreatedEvent,
    FileModifiedEvent,
    DirMovedEvent,
    FileMovedEvent, DirDeletedEvent, FileDeletedEvent, DirModifiedEvent)

from src.utils import remove_prefix, replace_backslashes


class EventHandler(FileSystemEventHandler):
    def __init__(self, port: str, base_path: str) -> None:
        self.port = port
        self.base_path = replace_backslashes(base_path)

    def dispatch(self, event):
        if replace_backslashes(event.src_path) != self.base_path:
            super().dispatch(event)
            time.sleep(0.2)

    @staticmethod
    def interpret_result(result: subprocess.CompletedProcess):
        if result.stderr:
            print("Operation failed:\n", result.stderr)
        elif b"Traceback (most recent call last)" in result.stdout:
            print("Operation failed:\n", result.stdout)
        else:
            print("Operation done successfully")

    def on_moved(self, event: Union[DirMovedEvent, FileMovedEvent]):
        src_path = remove_prefix(
            replace_backslashes(event.src_path), self.base_path)
        dest_path = replace_backslashes(event.dest_path)
        if ".goutputstream-" in src_path:
            result = subprocess.run([
                "mpremote",
                "connect",
                self.port,
                "resume",
                "cp",
                dest_path,
                f":{remove_prefix(dest_path, self.base_path)}",
            ], capture_output=True)
        else:
            dest_path = remove_prefix(dest_path, self.base_path)
            result = subprocess.run([
                "mpremote",
                "connect",
                self.port,
                "resume",
                "exec",
                f'from os import rename; rename("{src_path}", "{dest_path}")'
            ], capture_output=True)
        super().on_moved(event)
        return self.interpret_result(result)

    def on_created(self, event: Union[DirCreatedEvent, FileCreatedEvent]):
        src_path = replace_backslashes(event.src_path)
        if ".goutputstream-" in src_path:
            return
        if event.is_directory:
            result = subprocess.run([
                "mpremote",
                "connect",
                self.port,
                "resume",
                "mkdir",
                remove_prefix(src_path, self.base_path)
            ], capture_output=True)
        else:
            result = subprocess.run([
                "mpremote",
                "connect",
                self.port,
                "resume",
                "cp",
                src_path,
                f":{remove_prefix(src_path, self.base_path)}",
            ], capture_output=True)
        super().on_created(event)
        return self.interpret_result(result)

    def on_deleted(self, event: Union[DirDeletedEvent, FileDeletedEvent]):
        src_path = remove_prefix(
            replace_backslashes(event.src_path), self.base_path)
        result = subprocess.run([
            "mpremote",
            "connect",
            self.port,
            "resume",
            "rm",
            src_path
        ], capture_output=True)

        if b"[Errno 21] EISDIR" in result.stdout:
            result = subprocess.run([
                "mpremote",
                "connect",
                self.port,
                "resume",
                "rmdir",
                src_path
            ], capture_output=True)
        super().on_deleted(event)
        return self.interpret_result(result)

    def on_modified(self, event: Union[FileModifiedEvent, DirModifiedEvent]):
        src_path = replace_backslashes(event.src_path)
        if ".goutputstream-" in src_path:
            return

        if not event.is_directory:
            result = subprocess.run([
                "mpremote",
                "connect",
                self.port,
                "resume",
                "cp",
                src_path,
                f":{remove_prefix(src_path, self.base_path)}",
            ], capture_output=True)
            return self.interpret_result(result)
