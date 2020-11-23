from PyQt5 import QtCore, QtWidgets
import numpy as np
import matplotlib.gridspec as gridspec

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget
from IPython import embed


class RasterplotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings, sampling_rate, duration, grid_indices):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.fs = sampling_rate
        self.duration = duration
        self.grid_indices = grid_indices
        self.colors = ['#749800', '#006d7c']
        if len(grid_indices) > len(self.reader.spiketimes):
            self.spiketimes = self.reader.spiketimes
        else:
            self.spiketimes = self.reader.spiketimes
            self.spiketimes = [self.spiketimes[g_idx] for g_idx in self.grid_indices]
        self.plot_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        plot_name = 'Rasterplot_' + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):
        print(spike_mat)
        fs = self.fs
        rows = int(np.ceil(np.sqrt(len(spike_mat))))
        spec = gridspec.GridSpec(ncols=rows, nrows=rows, figure=fig)
        time_bin_range = range(1, int(self.duration) + int(self.duration/30), int(self.duration/30))
        spiketimes_for_plot = [[[] for j in range(len(time_bin_range))] for i in range(len(spike_mat))]
        for j in range(len(spike_mat)):
            for spike in spike_mat[j]:
                for s_i, s in enumerate(time_bin_range):
                    if spike > 1000:        # I try this to handle that spikes are stored as indices in SC file
                        spike = spike/fs
                    if (s - self.duration/30) <= spike <= s and spike not in spiketimes_for_plot[j][s_i]:
                        spiketimes_for_plot[j][s_i].append(spike - (s - self.duration/30))

        print(spiketimes_for_plot)
        for i in range(len(spiketimes_for_plot)):
            ax = fig.add_subplot(spec[i])
            for idx, spike_sublist in enumerate(reversed(spiketimes_for_plot[i])):
                if idx % 2 == 0:
                    c = self.colors[0]
                else:
                    c = self.colors[1]
                ax.scatter(spike_sublist/fs, np.ones(len(spike_sublist)) * idx, marker='|', color=c)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                labels = [item.get_text() for item in ax.get_yticklabels()]
                empty_string_labels = [''] * len(labels)
                ax.set_yticklabels(empty_string_labels)
                ax.set_ylabel('subdivided time of MEA channel')
                xlims = ax.get_xlim()
                ax.set_xticks([0, xlims[1]/2, xlims[1]])
                ax.set_xlim([0, xlims[1]])
                ax.set_xticklabels(['0', str((int(self.duration/30)/2)), str(int(self.duration/30))])
                ax.set_xlabel('time [s]')
                ax.get_xaxis().tick_bottom()
                ax.get_yaxis().tick_left()
                ax.tick_params(labelsize=10, direction='out')
            PlotManager.instance.add_plot(self.plot_widget)

    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
