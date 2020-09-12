from PyQt5 import QtCore, QtWidgets
import h5py
import os
import numpy as np


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super.__init__(parent)

        title = 'Settings'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.width = 300
        self.height = 200
        self.resize(self.width, self.height)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.setWindowTitle(title)