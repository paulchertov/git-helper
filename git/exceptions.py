class GitException(Exception):
    pass


class NotAGitRepository(GitException):
    pass


class NothingChanged(GitException):
    pass
