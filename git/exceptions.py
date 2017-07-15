class GitException(Exception):
    pass


class CmdException(Exception):
    pass


class NotAGitRepository(GitException):
    pass


class NothingChanged(GitException):
    pass
