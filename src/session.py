import os
import subprocess
import tempfile
import time

from watchdog.observers import Observer

from src.handler import EventHandler
from src.utils import open_dir


def _recursive_ls(port: str, path: str, files: list, dirs: list):
    result = subprocess.run([
        "mpremote",
        "connect",
        port,
        "resume",
        "ls",
        path
    ], capture_output=True)
    if b"failed to access" in result.stdout:
        return -1
    for item in result.stdout.decode().split("\r\n"):
        if not item.startswith(" "):
            continue
        item = item.lstrip(" ")
        if not item:
            continue
        size, filename = item.split(" ", maxsplit=1)
        if filename.endswith("/"):
            dirs.append(path + filename)
            result = _recursive_ls(
                port=port, path=path + filename,
                files=files, dirs=dirs)
            if result is not None:
                return result
        else:
            files.append(path + filename)


def _recursive_copy(dir_path, port: str):
    files = []
    dirs = []
    ls_result = _recursive_ls(
        port=port, path="/",
        files=files, dirs=dirs)
    if ls_result == -1:
        print("Syncing files failed :")
        print(f"Failed to access {port} (it may be in use by another program)")
        return ls_result

    for folder in dirs:
        os.makedirs(dir_path + folder, exist_ok=True)
    for i, file in enumerate(files):
        result = subprocess.run([
            "mpremote",
            "connect",
            port,
            "resume",
            "cp",
            f":{file}",
            dir_path + file
        ], capture_output=True)
        print(f"{(i + 1) * 100 // len(files)}% Completed")
    print("Synced files successfully")


def start_session(port: str):
    with tempfile.TemporaryDirectory() as tmp_dir_path:
        cp_result = _recursive_copy(dir_path=tmp_dir_path, port=port)
        if cp_result == -1:
            return
        observer = Observer()
        observer.schedule(
            EventHandler(port=port, base_path=tmp_dir_path),
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
