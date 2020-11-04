from PyQt5 import QtCore


class PlotCreationThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()

    def __init__(self, plot_widget, reader):
        super().__init__(plot_widget)
        self.plot_widget = plot_widget
        self.figure = self.plot_widget.figure
        self.reader = reader

    def run(self):
        self.finished.emit()
