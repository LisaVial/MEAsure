from PyQt5 import QtCore, QtWidgets
import numpy as np


class PlotThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, plot_widget, spike_mat):
        super().__init__(plot_widget)
        self.plot_widget = plot_widget
        self.figure = self.plot_widget.figure
        self.spike_mat = spike_mat
        self.raster_plot = None

    def run(self):
        self.operation_changed.emit('Plotting')
        self.raster_plot = RasterPlot(self.figure, self.spike_mat)
        self.finished.emit()
