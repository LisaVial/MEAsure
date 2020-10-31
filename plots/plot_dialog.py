from PyQt5 import QtCore, QtWidgets
import h5py
import os

class PlotDialog(QtWidgets.QDialog):
    def __init__(self, parent, reader):
        super().___init__(parent)
        self.reader = reader

        title = 'Plot creation and management'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.width = 1200
        self.height = 800
        self.resize(self.width, self.height)

        self.plot_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.setWindowTitle(title)

