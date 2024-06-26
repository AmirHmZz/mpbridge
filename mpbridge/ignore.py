import os

from . import utils


class IgnoreStorage:
    def __init__(self, dir_path: str):
        self._dirs = []
        self._files = []
        self._root_dir = dir_path.rstrip("/")
        self.load()

    def load(self):
        for subdir, dirs, files in os.walk(self._root_dir):
            subdir = utils.replace_backslashes(subdir)
            for file in files:
                if file == "mpbridge.ignore":
                    self._load_ignore_file(abs_dir=subdir.rstrip("/"))

    def _load_ignore_file(self, abs_dir: str):
        rel_dir = utils.remove_prefix(abs_dir, self._root_dir)
        try:
            with open(f"{abs_dir}/mpbridge.ignore", "r") as file:
                for line in utils.replace_backslashes(file.read()).split("\n"):
                    if not "".join(line.split()):
                        continue
                    line = "/" + line.lstrip("/")
                    if line.endswith("/"):
                        self._dirs.append(f"{rel_dir}{line.rstrip('/')}/")
                    else:
                        self._files.append(f"{rel_dir}{line}")
        except FileNotFoundError:
            pass
        except:
            raise RuntimeError("Invalid mpbridge.ignore file")

    def match_dir(self, rel_path: str) -> bool:
        rel_path = rel_path.rstrip("/") + "/"
        for ignored_dir in self._dirs:
            if rel_path.startswith(ignored_dir) or rel_path == ignored_dir:
                return True
        return False

    def match_file(self, rel_path: str) -> bool:
        if rel_path.endswith("mpbridge.hashtable"):
            return True
        for ignored_dir in self._dirs:
            if rel_path.startswith(ignored_dir):
                return True
        return rel_path in self._files
