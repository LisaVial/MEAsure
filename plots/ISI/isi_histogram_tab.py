from PyQt5 import QtCore, QtWidgets
import numpy as np
import seaborn as sns
import matplotlib.gridspec as gridspec

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class IsiHistogramTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings, sampling_rate, grid_labels, grid_indices):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.fs = sampling_rate
        self.grid_labels = grid_labels
        self.grid_indices = grid_indices
        if len(grid_indices) > len(self.reader.spiketimes):
            self.spiketimes = self.reader.spiketimes
        else:
            self.spiketimes = self.reader.spiketimes
            self.spiketimes = [self.spiketimes[g_idx] for g_idx in self.grid_indices]

        self.plot_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        plot_name = "ISI_histogram_" + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):
        rows = int(np.ceil(np.sqrt(len(spike_mat))))
        spec = gridspec.GridSpec(ncols=rows, nrows=rows, figure=fig, wspace=4 / rows, hspace=2 / rows)
        if spike_mat[0][0] > 100:  # this is not save, in the long run it should be changed, so that SC reader returns
            # actual spike times instead of indices
            spikes = np.array(spike_mat) / self.fs
        else:
            spikes = spike_mat
        interspike_intervals = []
        for spike_sublist in spikes:
            spikes_diff = np.diff(spike_sublist)
            interspike_intervals.append(spikes_diff)
        c = '#006d7c'
        sns.set_style('darkgrid')
        for i, isi_list in enumerate(interspike_intervals):
            ax = fig.add_subplot(spec[i])
            sns.histplot(isi_list, bins=11, color=c, ax=ax, kde=True)
            ax.set_xlim([0, int(np.max(isi_list))])
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.set_title(self.grid_labels[i], fontsize=10)
            ax.set_ylabel('count', fontsize=8)
            ax.set_xlabel('interspike interval [s]', fontsize=8)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()
            ax.tick_params(labelsize=8, direction='out')
        PlotManager.instance.add_plot(self.plot_widget)

    @staticmethod
    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
