import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog,\
    QWidget, QPushButton, QLabel, QLineEdit,\
    QGridLayout, QVBoxLayout

from git.git import PQGitSpeaker
from git.exceptions import NotAGitRepository, GitException
from controllers.file import PQFileListController


class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        self.result = ""
        # subcontrollers
        self.list = PQFileListController()
        self.git = PQGitSpeaker()

        # view
        self.view = QWidget()
        layout = QGridLayout()
        self.error_handler = QLabel()
        self.commit_message = QLineEdit()

        buttons_panel = QWidget()
        buttons_layout = QVBoxLayout()

        self.folder_button = QPushButton("Select folder")
        self.commit_button = QPushButton("Commit changes")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)

        buttons_layout.addWidget(self.folder_button)
        buttons_layout.addWidget(self.commit_button)
        buttons_layout.addWidget(self.refresh_button)

        buttons_panel.setLayout(buttons_layout)

        # putting it all together
        layout.addWidget(self.commit_message, 0, 0, 1, 1)
        layout.addWidget(self.list.view, 1, 0, 1, 1)
        layout.addWidget(self.error_handler, 2, 0, 1, 2)
        layout.addWidget(buttons_panel, 1, 1, 1, 1)

        self.view.setLayout(layout)

        self.setCentralWidget(self.view)
        self.show()

        # adding handlers to subcontrollers
        self.git.got_files.connect(self.got_files)
        self.git.error_occurred.connect(self.dispatch_error)

        # adding handlers to view
        self.folder_button.clicked.connect(self.select_folder)
        self.commit_button.clicked.connect(self.commit)
        self.refresh_button.clicked.connect(self.refresh)

    def select_folder(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            self.git.set_path(
                dlg.selectedFiles()[0].__repr__().strip("'")
            )

    def got_files(self, files):
        self.list.model = files

    def refresh(self):
        if self.git.path:
            self.git.get_files()
        else:
            self.dispatch_error(NotAGitRepository())

    @property
    def message(self):
        return self.commit_message.text()


    def commit(self):
        if self.message:
            self.git.push(self.list.model, self.message)
        else:
            self.error_handler.setText("nothing to commit")

    def dispatch_error(self, error):
        try:
            raise error
        except NotAGitRepository as e:
            self.git.abort()
            self.list.clear()
            self.error_handler.setText("Provide correct git repository folder")
        except GitException as e:
            self.error_handler.setText(str(e))

    def redraw(self):
        self.commit_button.setEnabled(
            bool(self.git.path and self.message)
        )
        self.refresh_button.setEnabled(
            bool(self.git.path)
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Test()
    sys.exit(app.exec_())