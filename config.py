"""
config file
"""

WIN_ENCODING = "cp866"  # standard console encoding
GIT_NOT_TRACKED_MARKER = """
(use "git checkout -- <file>..." to discard changes in working directory)
""".strip()  # standard git string before new/updated files section
GIT_TRACKED_NO_COMMIT_MARKER = """
(use "git add <file>..." to include in what will be committed)
""".strip()  # standard git string before new/updated files section when not added any commits
GIT_TRACKED_MARKER = """
(use "git reset HEAD <file>..." to unstage)
""".strip()  # standard git string before new/updated files already added to commit
NOT_GIT_MARKER = """
fatal: Not a git repository (or any of the parent directories): .git
""".strip()  # standard git string if path is not a git repository
