from . import utils


class IgnoreStorage:
    def __init__(self, dir_path: str):
        self._path = utils.remove_suffix(dir_path, "/") + "/"
        self._dirs = []
        self._files = []
        self._read_ignore_file()

    def _read_ignore_file(self):
        try:
            with open(f"{self._path}mpbridge.ignore", "r") as file:
                for line in utils.replace_backslashes(file.read()).split("\n"):
                    if not "".join(line.split()):
                        continue
                    line = "/" + line.lstrip("/")
                    if not line.endswith("/"):
                        self._files.append(line)
                    else:
                        self._dirs.append(line.rstrip("/") + "/")
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
        for ignored_dir in self._dirs:
            if rel_path.startswith(ignored_dir):
                return True
        return rel_path in self._files
