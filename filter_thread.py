from PyQt5 import QtCore
import numpy as np
import funcs

from mea_data_reader import MeaDataReader

class FilterThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, mea_file):
        super().__init__(parent)
        self.mea_file = mea_file
        self.filtered_file = None

    def filtering(self, file):
        pass

    def run(self):
        reader = MeaDataReader()
        file = reader.open_mea_file(self.mea_file)
        self.operation_changed.emit("Filtering traces")
        self.filtered_file = self.filtering(file)
        self.finished.emit()