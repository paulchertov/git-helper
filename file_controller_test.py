import sys
from typing import List

from PyQt5.uic import loadUi
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QGridLayout, QPushButton

from git.commands import GitStatusCommand
from git.git import PQGitSpeaker
from model.file import PQFileModel
from controllers.file import PQFileListController


class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        self.result = ""

        self.list = PQFileListController()
        self.git = PQGitSpeaker()

        self.git.got_files.connect(self.got_files)

        self.view = QWidget()
        layout = QGridLayout()
        button = QPushButton("Start")
        button.clicked.connect(self.test)

        layout.addWidget(self.list.view, 0, 0, 1, 1)
        layout.addWidget(button, 1, 0, 1, 1)

        self.view.setLayout(layout)

        self.setCentralWidget(self.view)
        self.view.show()
        self.list.view.show()
        button.show()
        self.show()

    def test(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            self.git.set_path(
                dlg.selectedFiles()[0].__repr__().strip("'")
            )

    def got_files(self, files):
        self.list.model = files


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Test()
    sys.exit(app.exec_())