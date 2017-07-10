from typing import List

from PyQt5.uic import loadUi
from PyQt5.QtCore import QObject, pyqtSlot

from model.file import PQFileModel


class PQFileListController(QObject):
    """
    Controller for list of git files widget
    """
    def __init__(self):
        super().__init__()
        self.__model = []
        self.view = loadUi("gui/git_file_list.ui")

    @pyqtSlot(list)
    def populate(self, files: List[PQFileModel]):
        """
        set model as copy of provided list (will differ with original
        git.git.PQGitSpeaker files list)
        :param files: list of PQFileModel to be copied
        :return: None
        """
        self.clear_view()
        self.__model = [file.copy() for file in files]
        for child_model in self.model:
            child_view = PQFileController(child_model).view
            self.view.layout().addWidget(child_view)
            child_view.show()

    @pyqtSlot
    def clear(self):
        """
        clear model and view
        :return: None
        """
        self.__model = []
        self.clear_view()

    def clear_view(self):
        """
        removes all widgets from view
        and deletes them
        :return: None
        """
        layout = self.view.layout()
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            layout.removeWidget(widget)
            widget.deleteLater()

    @property
    def model(self)->List[PQFileModel]:
        return self.__model

    @model.setter
    def model(self, val: List[PQFileModel]):
        self.populate(val)


# TODO: implement controller
class PQFileController(QObject):
    """
    Dummy for single file widget controller
    """
    def __init__(self, model: PQFileModel):
        super().__init__()
        self.__model = model