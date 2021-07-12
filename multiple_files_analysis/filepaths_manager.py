from PyQt5 import QtCore, QtWidgets
import os
import json


class FilepathsManager(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)