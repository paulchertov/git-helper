import sys
import os
from typing import List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QFrame
from PyQt5.uic import loadUi

from git import PQGitSpeaker, NotAGitRepository, GitException
from controllers import PQFileListController
from model.file import PQFileModel


class PQGitHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.result = ""

        # subcontrollers
        self.list = PQFileListController()
        self.git = PQGitSpeaker()

        # view
        self.view = QFrame()
        self.view = loadUi("gui/main.ui", self.view)

        # setting styles
        style_path = os.path.join('gui', 'main.qss')
        style_path = os.path.abspath(style_path)
        self.view.setStyleSheet(open(style_path, 'r').read())

        # adding subcontrollers view
        self.view.layout().addWidget(self.list.view, 1, 0, 1, 2)

        self.setCentralWidget(self.view)
        self.show()

        # adding handlers to subcontrollers
        self.git.got_files.connect(self.got_files)
        self.git.error_occurred.connect(self.dispatch_error)

        # adding handlers to view
        self.view.folder_button.clicked.connect(self.select_folder)
        self.view.commit_button.clicked.connect(self.commit)
        self.view.refresh_button.clicked.connect(self.refresh)
        self.view.commit_message.textChanged.connect(self.redraw)

        self.redraw()

    @property
    def message(self)->str:
        return self.view.commit_message.text()

    @pyqtSlot()
    def select_folder(self):
        """
        Handler for select button.
        Renders dialog for folder selection
        :return: 
        """
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            self.git.set_path(
                dlg.selectedFiles()[0].__repr__().strip("'")
            )
        self.redraw()

    @pyqtSlot(list)
    def got_files(self, files: List[PQFileModel]):
        """
        Handler for PQGitSpeaker.got_files signal.
        Renders files to PQFilesListController's view
        :param files: list of PQFileModel got from git
        :return: None
        """
        self.list.model = files

    @pyqtSlot()
    def refresh(self):
        """
        Handler for refresh button. Removes output text and
        tries to refresh folders files if path is set
        :return: None
        """
        self.view.output.setText("")
        self.redraw()
        if self.git.path:
            self.git.get_files()
        else:
            self.dispatch_error(NotAGitRepository())

    @pyqtSlot()
    def commit(self):
        """
        Handler for commit button.
        tries to commit changes to git
        :return: None
        """
        if self.message:
            self.git.push(self.list.model, self.message)
        else:
            self.view.output.setText("nothing to commit")

    @pyqtSlot(GitException)
    def dispatch_error(self, error: GitException):
        """
        Handler for PQGitSpeaker.error_occurred signal.
        Displays corresponding error to self.view.output
        :param error: error that occurred in PQGitSpeaker
        :return: None
        """
        try:
            raise error
        except NotAGitRepository:
            self.git.abort()
            self.list.clear()
            self.view.output.setText("Provide correct git repository folder")
        except GitException as e:
            self.view.output.setText(str(e))
        self.redraw()

    @pyqtSlot()
    def redraw(self):
        """
        Enables or disables control buttons depending on controllers state
        :return: None
        """
        self.view.commit_button.setEnabled(
            bool(self.git.path and self.message)
        )
        self.view.refresh_button.setEnabled(
            bool(self.git.path)
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PQGitHelper()
    sys.exit(app.exec_())