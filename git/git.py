from typing import List

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from .cmd import PQCmd
from .commands import ConsoleCommand, GitStatusCommand, GitCommitSequenceCommand
from .exceptions import CmdException


class PQGitSpeaker(QObject):
    """
    Facade, providing API for Cmd speaking thread
    """

    # outer signals
    aborted = pyqtSignal()
    error_occurred = pyqtSlot(CmdException)
    got_files = pyqtSignal(list)
    pushed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.cmd = PQCmd()
        self.cmd.start()
        self.__path = None
        self.__files = []
        self.cmd.executed.connect(self.dispatch)

    def reset(self):
        """
        Reset all changes
        :return: None
        """
        self.__path = None
        self.__files = []

    def push(self, file_paths: List[str], message: str):
        """
        :param message: commit message
        :param file_paths: list of relative files paths to commit 
        :return: None 
        """
        self.cmd.execute(
            GitCommitSequenceCommand(self.__path, file_paths, message)
        )

    @pyqtSlot(str)
    def set_path(self, path):
        """
        set path and refresh files
        :param path: git folder path
        :return: None
        """
        self.__path = path
        self.get_files()

    @pyqtSlot()
    def abort(self):
        """
        stop everything and reset object
        :return: None
        """
        self.reset()
        self.cmd.abort()
        self.aborted.emit()

    @pyqtSlot()
    def get_files(self):
        self.cmd.execute(GitStatusCommand(self.__path))

    @pyqtSlot(ConsoleCommand)
    def dispatch(self, executed_command: ConsoleCommand):
        if isinstance(executed_command.result, CmdException):
            self.error_occurred.emit(executed_command.result)

        if isinstance(executed_command, GitStatusCommand):
            self.__files = executed_command.result
            self.got_files.emit(executed_command.result)

        elif isinstance(executed_command, GitCommitSequenceCommand):
            self.pushed.emit()
            self.get_files()  # refresh changes
