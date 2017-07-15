from typing import Iterable

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from model.file import PQFileModel
from .cmd import PQCmd
from .commands import ConsoleCommand, GitStatusCommand, GitCommitSequenceCommand
from .exceptions import GitException, NothingChanged


class PQGitSpeaker(QObject):
    """
    Facade, providing API for Cmd speaking thread
    """

    # signals
    aborted = pyqtSignal()
    error_occurred = pyqtSignal(GitException)
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

    def push(self, files: Iterable[PQFileModel], message: str):
        """
        :param message: commit message
        :param files: list of files with their state tu actualize 
        :return: None 
        """
        tracked_in_git = set()
        not_tracked_in_git = set()
        user_wants_to_add = set()
        user_dont_want_to_add = set()

        for file in self.files:
            if file.tracked:
                tracked_in_git.add(file.path)
            else:
                not_tracked_in_git.add(file.path)

        for file in files:
            if file.tracked:
                user_wants_to_add.add(file.path)
            else:
                user_dont_want_to_add.add(file.path)

        files_to_commit = user_wants_to_add - tracked_in_git
        files_to_reset = user_dont_want_to_add - not_tracked_in_git

        commit_changes = tracked_in_git | files_to_commit | files_to_reset

        if not commit_changes:
            self.error_occurred.emit(NothingChanged())
        else:
            self.cmd.execute(
                GitCommitSequenceCommand(
                    self.__path,
                    files_to_commit,
                    files_to_reset,
                    message)
            )

    @pyqtSlot(str)
    def set_path(self, path: str):
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
        print(self.__path)
        self.cmd.execute(GitStatusCommand(self.__path))

    @pyqtSlot(ConsoleCommand)
    def dispatch(self, executed_command: ConsoleCommand):
        if isinstance(executed_command.result, GitException):
            self.error_occurred.emit(executed_command.result)
            return

        if isinstance(executed_command, GitStatusCommand):
            self.__files = executed_command.result
            self.got_files.emit(executed_command.result)

        elif isinstance(executed_command, GitCommitSequenceCommand):
            self.pushed.emit()
            self.get_files()  # refresh changes

    @property
    def files(self):
        return self.__files

    @property
    def path(self):
        return self.__path
