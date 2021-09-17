from PyQt5 import QtCore, QtWidgets
import numpy as np
import matplotlib.gridspec as gridspec
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget
from utility import channel_utility
from IPython import embed


class RasterplotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings, sampling_rate, duration, grid_labels, grid_indices, mcs_channel_ids):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.fs = sampling_rate
        self.duration = duration
        self.grid_labels = grid_labels
        self.grid_indices = grid_indices
        self.colors = ['#749800', '#006d7c']
        self.dead_channels = []
        if 'SC' in str(self.reader):
            self.dead_channels = self.reader.dead_channels

        self.spiketimes = []

        for mcs_index in self.grid_indices:
            if mcs_index in self.dead_channels:
                self.spiketimes.append(np.array([]))
            else:
                self.spiketimes.append(self.reader.spiketimes[channel_utility.ChannelUtility.get_sc_index(
                    mcs_index, self.dead_channels)])

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        plot_name = 'Rasterplot_' + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):

        # determine how many grid labels to skip
        label_step_size = max(1, int(np.ceil(len(spike_mat) / 16.0)))

        sns.set()
        fs = self.fs
        ax = fig.add_subplot(111)
        # spike_mat.reverse()
        sts = np.flip(spike_mat)
        ax.eventplot(sts/fs)
        if len(self.grid_labels) == 1:
            ax.set_yticks([1.0])
            ax.set_yticklabels([self.grid_labels[0]])
        else:
            ax.set_yticks(np.arange(0, len(self.grid_labels), label_step_size))
            ax.set_yticklabels(self.grid_labels[(len(self.grid_labels) -1)::-label_step_size])
        ax.set_ylabel('MEA channels')
        ax.set_xlabel('time [s]')
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax.tick_params(labelsize=10, direction='out')
        PlotManager.instance.add_plot(self.plot_widget)

    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
