import re
from collections import namedtuple
from enum import Enum

from config import GIT_NOT_TRACKED_MARKER, GIT_TRACKED_MARKER


is_file = re.compile("\t((?:modified:)|(?:new\sfile:))?[\s]*(.+)")


StatusStates = Enum('StatusStates', 'BEFORE_ALL NOT_TRACKED TRACKED')


File = namedtuple('File', 'tracked modified name')


def _add_if_file(tracked: bool, repr: str, to: list):
    """
    Internal function. If repr looks like a file adds it to result
    :param tracked: is file already tracked by git 
    :param repr: line that may represent a file
    :param to: list of results where file should be appended
    :return: None
    """
    match = is_file.match(repr)
    if len(match.group) == 2:
        to.append(File(
            tracked=tracked,
            modified=True if match.group(0) == "modified:" else False,
            name=match.group(1)
        ))


def map_status(answer: str):
    """
    Mapper for 'git status' console response
    :param answer: result of 'git status' command
    :return: list of File named tuples
    """
    state = StatusStates.BEFORE_ALL
    lines = answer.split("\n")
    result = []
    for line in lines:
        if state is StatusStates.BEFORE_ALL:
            if line == GIT_NOT_TRACKED_MARKER:
                state = StatusStates.NOT_TRACKED
        elif state == StatusStates.NOT_TRACKED:
            if line == GIT_TRACKED_MARKER:
                state = StatusStates.TRACKED
            else:
                _add_if_file(False, line, result)
        elif state is StatusStates.TRACKED:
            _add_if_file(True, line, result)
    return result
