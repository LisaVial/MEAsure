from PyQt5 import QtWidgets
import numpy as np
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class SpikeTimePlot(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, label, label_index):
        super().__init__(parent)
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.label = label
        self.label_index = label_index

        main_layout = QtWidgets.QVBoxLayout(self)

        plot_name = 'SpikeTimePlot_' + self.mcs_reader.filename + '_' + self.label

        plot_widget = PlotWidget(self, plot_name)
        sns.set()
        self.figure = plot_widget.figure
        self.ax = self.figure.add_subplot(111)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()
        self.ax.tick_params(labelsize=10, direction='out')
        self.ax.set_xlabel('time [msec]')
        self.ax.set_ylabel(r'voltage [$\mu$ V]')

        self.plot(self.label)
        main_layout.addWidget(plot_widget)

    def plot(self, label):
        pass