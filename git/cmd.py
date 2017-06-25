from subprocess import Popen, PIPE

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread

from config import WIN_ENCODING
from .commands import ConsoleCommand


class PQCmd(QThread):
    """
    Background thread for dealing with cmd queries
    """
    executed = pyqtSignal(ConsoleCommand)
    aborted = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__dead = False
        self.__commands = []

    def run(self):
        while not self.__dead:
            while self.__commands:
                self.__execute(self.__commands.pop(0))
            self.sleep(1)

    def execute(self, command: ConsoleCommand):
        self.__commands.append(command)

    @pyqtSlot()
    def kill(self):
        self.__dead = True
        self.aborted.emit()

    @pyqtSlot()
    def abort(self):
        self.__commands = []
        self.aborted.emit()

    def __execute(self, command: ConsoleCommand):
        print(command.text)
        process = Popen(command.text, stdin=PIPE, stdout=PIPE, shell=True)
        command.result = process.communicate()[0].decode(WIN_ENCODING)
        self.executed.emit(command)

    def __del__(self):
        self.wait()
