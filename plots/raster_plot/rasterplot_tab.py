from PyQt5 import QtCore, QtWidgets
import numpy as np

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
        fs = self.fs
        ax = fig.add_subplot(111)
        for i in reversed(range(len(spike_mat))):
            spiketimes_for_plot = []
            for spike in spike_mat[i]:
                for s in range(self.duration, int(self.duration/30)):
                    spiketimes_for_plot.append([])
                    if spike <= s:
                        spiketimes_for_plot.append(spike)
            # embed()

            if i % 2 == 0:
                c = self.colors[0]
            else:
                c = self.colors[1]
            ax.scatter(spike_mat[i]/fs, np.ones(len(spike_mat[i])) * i, marker='|', color=c)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        labels = [item.get_text() for item in ax.get_yticklabels()]
        empty_string_labels = [''] * len(labels)
        ax.set_yticklabels(empty_string_labels)
        ax.set_ylabel('MEA channels')
        xlims = ax.get_xlim()
        ax.set_xticks([0, xlims[1]/2, xlims[1]])
        ax.set_xlim([0, xlims[1]])
        ax.set_xticklabels(['0', str(int(np.ceil(self.duration/2))), str(int(np.ceil(self.duration)))])
        ax.set_xlabel('time [s]')
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax.tick_params(labelsize=10, direction='out')
        PlotManager.instance.add_plot(self.plot_widget)

    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
