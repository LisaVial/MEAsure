from PyQt5 import QtCore


class PlotCreationThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, plot_widget, reader):
        super().__init__(plot_widget)
        self.plot_widget = plot_widget
        self.figure = self.plot_widget.figure
        self.reader = reader
        self.csd_plot = None

    def run(self):
        self.operation_changed.emit('Plotting')
        # self.csd_plot = CsdPlot(self.figure, self.reader)
        # self.raster_plot = RasterPlot(self.figure, self.spike_mat)
        self.finished.emit()