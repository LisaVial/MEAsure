from PyQt5 import QtCore, QtWidgets
import numpy as np
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class RawTraceWThresholdPlot(QtWidgets.QWidget):
    def __init__(self, parent, reader, label):
        super().__init__(parent)
        self.reader = reader
        self.label = label
        main_layout = QtWidgets.QVBoxLayout(self)

        plot_name = 'SpikeVerification_RawTracewThreshold_' + self.reader.filename + '_' + self.label

        plot_widget = PlotWidget(self, plot_name)
        self.figure = plot_widget.figure
        self.ax = self.figure.add_subplot(111)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()
        self.ax.tick_params(labelsize=10, direction='out')
        self.ax.set_xlabel('time [sec]')
        self.ax.set_ylabel(r'voltage [$\mu$ V]')
        self.plot(self.label)
        main_layout.addWidget(plot_widget)

    def plot(self, label):
        scaled_trace = self.reader.get_scaled_channel(label)
        fs = self.reader.sampling_frequency
        time = np.arange(0, len(scaled_trace)/fs, 1/fs)
        # ToDo: add filtering like it is done by Spyking circus
        self.ax.cla()
        self.ax.plot(time, scaled_trace)
        self.figure.canvas.draw_idle()
