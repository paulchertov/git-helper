import re
from typing import Union, List, Iterable, Any
from enum import Enum

from config import GIT_NOT_TRACKED_MARKER, GIT_TRACKED_MARKER,\
    NOT_GIT_MARKER, GIT_TRACKED_NO_COMMIT_MARKER
from git.exceptions import GitException, NotAGitRepository
from model.file import PQFileModel


class ConsoleCommand:
    """
    Simple wrapper for one Windows console command
    """
    def __init__(self, text: Union[str, List[str]]):
        """
        :param text: text of command or list of command texts
        """
        self.text = text if isinstance(text, str) else " && ".join(text)
        self.__result = None

    def map_result(self, answer: str, error: str) -> Union[Any, GitException]:
        """
        :param answer: stdout content as a string of the result of the command's execution 
        :param error: stderr content as a string of what happened during execution
        :return: resulting value if everything is ok or CmdException if error occurred 
        """
        return answer if not error else GitException(error)

    @property
    def result(self)->Any:
        """
        :return: result of command execution
        """
        return self.__result

    def set_result(self, answer: str, error: str):
        """
        :param answer: 
        :param error: 
        :return: 
        """
        self.__result = self.map_result(answer, error)


class FolderCommand(ConsoleCommand):
    """
    Class for console command that operates in particular folder
    and needs path of that folder to be set
    """
    is_path = re.compile(r"(\w:)([/\\].*)")

    def __init__(self, path: str, text: Union[str, List[str]]):
        """
        :param path: path to folder where commands should be ran
        :param text: text of command or list of command texts
        """
        parsed_path = self.is_path.match(path)
        if parsed_path is None:
            raise ValueError("{} not seem like path".format(path))
        partition, folder = parsed_path.groups()
        if isinstance(text, str):
            text = text.split(" && ")
        super().__init__(
            [
                partition,
                "cd " + folder
            ] + text)


class GitStatusCommand(FolderCommand):
    """
    'git status' command that returns files in directory:
    newly created and updated, tracked and not yet added to git
    """
    is_file = re.compile(
        r"\t((?:modified:)|(?:new\sfile:)|(?:deleted:)|(?:renamed:))?[\s]*(.+)"
    )

    StatusStates = Enum('StatusStates', 'BEFORE_ALL NOT_TRACKED TRACKED')

    def __init__(self, path: str):
        """
        :param path: path to the git folder
        """
        super().__init__(path, "git status")

    def map_result(self, answer: str, error: str)\
            -> Union[List[PQFileModel], GitException]:
        """
        Mapper for 'git status' console response extracting files
        from cmd answer
        :param answer: stdout string of 'git status' command
        :param error: stderr string of 'git status' command
        :return: list of File named tuples or CmdException exception
        """

        if error:
            if NOT_GIT_MARKER in error:
                return NotAGitRepository()
            else:
                return GitException(error)

        state = self.StatusStates.BEFORE_ALL
        lines = answer.split("\n")
        result = []

        def _add_if_file(tracked: bool, line: str):
            """
            If line looks like a file adds it to result
            :param tracked: is file already tracked by git 
            :param line: line that may represent a file
            """
            match = self.is_file.match(line)
            if match is not None:
                result.append(PQFileModel(
                    tracked=tracked,
                    status=match.group(1),
                    path=match.group(2)
                ))

        for line in lines:
            if state is self.StatusStates.BEFORE_ALL:
                if GIT_TRACKED_MARKER in line:
                    state = self.StatusStates.TRACKED
                if GIT_NOT_TRACKED_MARKER in line \
                        or GIT_TRACKED_NO_COMMIT_MARKER in line:
                    state = self.StatusStates.NOT_TRACKED

            elif state == self.StatusStates.NOT_TRACKED:
                if GIT_TRACKED_MARKER in line:
                    state = self.StatusStates.TRACKED
                else:
                    _add_if_file(False, line)

            elif state is self.StatusStates.TRACKED:
                if GIT_NOT_TRACKED_MARKER in line:
                    state = self.StatusStates.NOT_TRACKED
                else:
                    _add_if_file(True, line)

        return result


class GitCommitSequenceCommand(FolderCommand):
    """
    Sequence of commands, needed to commit changes:
    'git add' for each file
    'git commit -m "%message%"'
    'git push'
    """
    def __init__(self, path: str, files_to_commit: Iterable[str],
                 files_to_reset: Iterable[str], message: str):
        """
        :param path: path to the git folder 
        :param files_to_commit: list of relative paths to files to be committed
        :param files_to_reset: list of relative paths to files to be removed from commit
        :param message: commit message
        """
        commands_sequence = \
            [
                "git add " + file_path for file_path in files_to_commit
            ] + [
                "git reset " + file_path for file_path in files_to_reset
            ] + [
                'git  commit -m "{}"'.format(message.replace('"', "'")),
                "git push"
            ]
        super().__init__(path, commands_sequence)

    def map_result(self, answer: str, error: str) -> Union[None, GitException]:
        """
        :param answer: cmd stdout string
        :param error:  cmd stderr string
        :return: None if everything is ok, CmdException otherwise
        """
        return None if not error else GitException(error)