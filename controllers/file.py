import os
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

        # loading view
        view_path = os.path.join('gui', 'git_file_list.ui')
        view_path = os.path.abspath(view_path)
        self.view = loadUi(view_path)

        # setting styles
        style_path = os.path.join('gui', 'git_file_list.qss')
        style_path = os.path.abspath(style_path)
        self.view.setStyleSheet(open(style_path, 'r').read())



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
            self.view.children_layout.addWidget(child_view)
            child_view.show()

    @pyqtSlot()
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
        layout = self.view.children_layout
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


class PQFileController(QObject):
    def __init__(self, model: PQFileModel):
        """
        :param model: PQFileModel of controller 
        """
        super().__init__()
        self.__model = model
        self.__model.changed.connect(self.redraw)

        # loading view
        view_path = os.path.join('gui', 'git_file.ui')
        view_path = os.path.abspath(view_path)
        self.view = loadUi(view_path)

        # adding handlers
        self.add_view_handlers()
        self.view.committed.clicked.connect(self.checkbox_clicked)

        # setting styles
        style_path = os.path.join('gui', 'git_file.qss')
        style_path = os.path.abspath(style_path)
        self.view.setStyleSheet(open(style_path, 'r').read())

        self.redraw()

    @pyqtSlot(bool)
    def checkbox_clicked(self, state: bool):
        self.__model.tracked = state

    def add_view_handlers(self):
        """  
        this method exists because of a weird glitch: while gui contained in
        separate attribute, method slots are not working if not added to 
        gui object
        :return: None
        """
        self.view.checkbox_clicked = self.checkbox_clicked

    @pyqtSlot()
    def redraw(self):
        """
        set actual model attributes to view widgets
        :return: None
        """
        self.view.status.setText(
            self.__model.status.name
        )
        self.view.path.setText(self.__model.path)
        self.view.committed.setChecked(1 if self.__model.tracked else 0)
        self.view.show()

