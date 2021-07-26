from PyQt5 import QtCore, QtGui, QtWidgets


class WorkerThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.function = None
        self.args = ()
        self.kwargs = dict()
        self.result = None

    def set_function(self, function):
        self.function = function

    def set_arguments(self, *args, **kwargs):
        self.args = args    # regular arguments
        self.kwargs = kwargs    # keyword arguments

    def run(self):
        if self.function:
            self.result = self.function(*self.args, **self.kwargs)
        self.finished.emit()

    def get_result(self):
        return self.result
