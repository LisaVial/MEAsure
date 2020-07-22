from PyQt5 import QtCore, QtWidgets
import time

from raster_plot import RasterPlot


class PlotCreationThread(QtCore.QThread):
    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, n, plot_widget, figure, spike_mat):
        super().__init__(plot_widget)
        self.plot_widget = plot_widget
        self.figure = figure
        self.spike_mat = spike_mat
        self.n = n

    def run(self):
        self.total.emit(self.n)
        i = 0
        self.raster_plot.plot(self.figure, self.spike_mat)
        self.plot_widget.refresh_canvas()
        while i < self.n:
            if time.time() % 1 == 0:
                i += 1
                self.update.emit()


class Progress(QtWidgets.QProgressBar):

    def __init__(self, parent=None):
        super(Progress, self).__init__(parent)
        self.setValue(0)

        self.thread = PlotCreationThread(self, 3)

        self.thread.total.connect(self.setMaximum)
        self.thread.update.connect(self.update)
        self.thread.finnished.connect(self.close)

        self.n = 0
        self.thread.start()

    def update(self):
        self.n += 1
        print(self.n)
        self.setValue(self.n)
