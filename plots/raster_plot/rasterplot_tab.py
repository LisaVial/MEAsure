from PyQt5 import QtCore, QtWidgets
import numpy as np
import matplotlib.gridspec as gridspec
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget
from IPython import embed


class RasterplotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings, sampling_rate, duration, grid_labels, grid_indices):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.fs = sampling_rate
        self.duration = duration
        self.grid_labels = grid_labels
        self.grid_indices = grid_indices
        self.colors = ['#749800', '#006d7c']
        if len(grid_indices) > len(self.reader.spiketimes):
            self.spiketimes = self.reader.spiketimes
        else:
            self.spiketimes = self.reader.spiketimes
            self.spiketimes = [self.spiketimes[g_idx] for g_idx in self.grid_indices]

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        plot_name = 'Rasterplot_' + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):
        sns.set()
        fs = self.fs
        ax = fig.add_subplot(111)
        sts = np.array(spike_mat)
        ax.eventplot(sts/fs)
        ax.set_yticks(range(0, len(self.grid_labels), 16))
        ax.set_yticklabels(self.grid_labels[::16])
        ax.set_ylabel('MEA channels')
        ax.set_xlabel('time [s]')
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax.tick_params(labelsize=10, direction='out')
        PlotManager.instance.add_plot(self.plot_widget)

    @staticmethod
    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
