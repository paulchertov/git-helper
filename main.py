import sys
import time

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from git.cmd import PQCmd, ConsoleCommand


class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        self.result = ""
        loadUi("gui/cmd_test.ui", self)
        self.start_button.clicked.connect(self.test)
        self.cmd = PQCmd()
        self.cmd.executed.connect(self.cmd_dispatch)
        self.cmd.start()
        self.show()

    def test(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            self.cmd.execute(
                ConsoleCommand([
                    "cd " + dlg.selectedFiles()[0].__repr__()[3:-1],
                    "dir"
                ])
            )
            time.sleep(1)
            self.cmd.execute(
                ConsoleCommand("dir")
            )

    def cmd_dispatch(self, command):
        self.result += command.result
        self.output.setText(self.result)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Test()
    sys.exit(app.exec_())
