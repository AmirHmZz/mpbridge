from typing import Union

from watchdog.events import (
    FileSystemEventHandler,
    DirCreatedEvent,
    FileCreatedEvent,
    FileModifiedEvent,
    DirMovedEvent,
    FileMovedEvent,
    DirDeletedEvent,
    FileDeletedEvent,
    DirModifiedEvent)

from .pyboard import SweetPyboard
from .utils import remove_prefix, replace_backslashes


class EventHandler(FileSystemEventHandler):
    def __init__(self, pyb: SweetPyboard, base_path: str) -> None:
        self.pyb = pyb
        self.base_path = replace_backslashes(base_path)

    def dispatch(self, event):
        if replace_backslashes(event.src_path) != self.base_path:
            super().dispatch(event)

    def on_moved(self, event: Union[DirMovedEvent, FileMovedEvent]):
        src_path = remove_prefix(
            replace_backslashes(event.src_path), self.base_path)
        dest_path = replace_backslashes(event.dest_path)
        rel_dest_path = remove_prefix(dest_path, self.base_path)
        if ".goutputstream-" in src_path:
            self.pyb.fs_verbose_put(dest_path, rel_dest_path)
        else:
            self.pyb.fs_verbose_rename(src_path, rel_dest_path)
        super().on_moved(event)

    def on_created(self, event: Union[DirCreatedEvent, FileCreatedEvent]):
        src_path = replace_backslashes(event.src_path)
        rel_src_path = remove_prefix(src_path, self.base_path)
        if ".goutputstream-" in src_path:
            return
        if event.is_directory:
            self.pyb.fs_verbose_mkdir(rel_src_path)
        else:
            self.pyb.fs_verbose_put(src_path, rel_src_path)
        super().on_created(event)

    def on_deleted(self, event: Union[DirDeletedEvent, FileDeletedEvent]):
        src_path = remove_prefix(
            replace_backslashes(event.src_path), self.base_path)
        try:
            self.pyb.fs_verbose_rm(src_path)
        except:
            self.pyb.fs_verbose_rmdir(src_path)
        super().on_deleted(event)

    def on_modified(self, event: Union[FileModifiedEvent, DirModifiedEvent]):
        src_path = replace_backslashes(event.src_path)
        rel_src_path = remove_prefix(src_path, self.base_path)
        if ".goutputstream-" in src_path:
            return
        if not event.is_directory:
            self.pyb.fs_verbose_put(src_path, rel_src_path)
