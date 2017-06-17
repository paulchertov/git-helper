from subprocess import Popen, PIPE

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread


class ConsoleCommand:
    """
    Simple wrapper for one Windows console command
    """
    def __init__(self, text, map_result=None):
        """
        :param text: text of command or list of command texts
        :type text: Union(str | list[str])
        :param map_result: callable for filtering a
        :type: map_result: callable
        """
        self.text = text if isinstance(text, str) else " && ".join(text)
        self.__map_result = map_result or (lambda x: x)
        self.__result = None

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, val):
        self.__result = self.__map_result(val)


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

    def execute(self, command):
        self.__commands.append(command)

    @pyqtSlot()
    def kill(self):
        self.__dead = True
        self.aborted.emit()

    @pyqtSlot()
    def abort(self):
        self.__commands = []
        self.aborted.emit()

    def __execute(self, command):
        print(command.text)
        process = Popen(command.text, stdin=PIPE, stdout=PIPE, shell=True)
        command.result = process.communicate()[0].decode('cp866')
        self.executed.emit(command)

    def __del__(self):
        self.wait()
