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
        """
        add command for execution
        :param command: 
        :return: 
        """
        self.__commands.append(command)

    @pyqtSlot()
    def kill(self):
        """
        stop thread
        :return: None
        """
        self.__dead = True
        self.aborted.emit()

    @pyqtSlot()
    def abort(self):
        """
        abort all planned actions
        :return: None
        """
        self.__commands = []
        self.aborted.emit()

    def __execute(self, command: ConsoleCommand):
        """
        execute particular console command
        :param command: command to execute
        :return: None
        """
        print(command.text)
        process = Popen(command.text, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        command.set_result(*map(lambda x: x.decode(WIN_ENCODING), process.communicate()))
        self.executed.emit(command)

    def __del__(self):
        self.wait()
