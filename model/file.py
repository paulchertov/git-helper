from typing import Union
from enum import Enum

from PyQt5.QtCore import QObject, pyqtSignal


FileStatus = Enum('FileCondition', 'new modified deleted')


class PQFileModel(QObject):
    changed = pyqtSignal()
    status_mapping = {
        "new file": FileStatus.new,
        "modified": FileStatus.modified,
        "deleted": FileStatus.deleted
    }

    def __init__(self, tracked: bool, status: Union[str, FileStatus],
                 path: str):
        super().__init__()
        self.__tracked = tracked
        if not status:
            self.__status = FileStatus.new
        elif isinstance(status, FileStatus):
            self.__status = status
        else:
            status = status.replace(":", "")
            self.__status = self.status_mapping[status]
        self.__path = path

    def copy(self):
        return PQFileModel(self.tracked, self.status, self.name)

    @property
    def tracked(self)->bool:
        return self.__tracked

    @tracked.setter
    def tracked(self, val: bool):
        self.__tracked = val
        self.changed.emit()

    @property
    def status(self) -> FileStatus:
        return self.__status

    @status.setter
    def status(self, val: FileStatus):
        self.__status = val
        self.changed.emit()

    @property
    def path(self) -> str:
        return self.__path

    @path.setter
    def path(self, val: str):
        self.__path = val
        self.changed.emit()

    def update(self, tracked: Union[bool, None]=None,
               status: Union[FileStatus, None]=None,
               path: Union[str, None]=None):
        if tracked is not None:
            self.__tracked = tracked
        if status is not None:
            self.__status = status
        if path is not None:
            self.__path = path
        self.changed.emit()

    def __repr__(self):
        return "<FileModel: status={}, tracked={}, path='{}'>\n".format(
            self.status.name, self.tracked, self.path
        )
