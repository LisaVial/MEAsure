from PyQt5 import QtCore, QtWidgets
import numpy as np

from plots.plot_settings import PlotSettings
from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class HeatmapTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.colors = ['#749800', '#006d7c']

        self.spiketimes = self.reader.spiketimes
        self.plot_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        plot_name = 'Rasterplot_' + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):
        fs = 10000
        ax = fig.add_subplot(111)
        print(type(spike_mat))
