from PyQt5 import QtCore, QtWidgets


class HilbertTransformTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_indices, settings):
        super().__init__(parent)
        self.reader = reader
        self.grid_indices = grid_indices
        self.settings = settings