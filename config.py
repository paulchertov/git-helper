"""
config file
"""

WIN_ENCODING = "cp866"  # standard console encoding
GIT_NOT_TRACKED_MARKER = """
(use "git checkout -- <file>..." to discard changes in working directory)
""".strip()  # standard git string before new/updated files section
GIT_TRACKED_MARKER = """
(use "git reset HEAD <file>..." to unstage)
""".strip()  # standard git string before new/updated files already added to commit
