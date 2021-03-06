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

        # plot_name = 'Rasterplot_' + self.reader.filename

        self.plot_widget = PlotWidget(self, 'Rasterplot')
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):
        # ToDo: redo this whole plot, since the binning of 10 sec segments per row does not make a lot of sense
        sns.set()
        fs = self.fs
        rows = int(np.ceil(np.sqrt(len(spike_mat))))
        spec = gridspec.GridSpec(ncols=rows, nrows=rows, figure=fig)
        time_bin_range = range(10, int(self.duration) + int(self.duration/30), int(self.duration/30))
        spiketimes_for_plot = [[[] for j in range(len(time_bin_range))] for i in range(len(spike_mat))]
        to_row_major_order = (lambda idx, rows: ((idx - 1) % rows) * rows + int((idx - 1) / rows) + 1)
        y_labels = []
        for j in range(len(spike_mat)):
            for spike in spike_mat[j]:
                for s_i, s in enumerate(time_bin_range):
                    if s % 10 == 0 and s not in y_labels:
                        y_labels.append(s)
                    if spike > 1000:        # I try this to handle that spikes are stored as indices in SC file
                        spike = spike/fs
                    if (s - self.duration/30) <= spike <= s and spike not in spiketimes_for_plot[j][s_i]:
                        spiketimes_for_plot[j][s_i].append(spike - (s - self.duration/30))
        for i in range(len(spiketimes_for_plot)):
            # try to flatten axes objects by using axes_objects.flatten(order='F') -> this will flatten in column major
            # order
            row_major_order_idx = to_row_major_order(i, rows)
            ax = fig.add_subplot(spec[i])
            for idx, spike_sublist in enumerate(reversed(spiketimes_for_plot[i])):
                if idx % 2 == 0:
                    c = self.colors[0]
                else:
                    c = self.colors[1]
                ax.scatter(np.array(spike_sublist)/fs, np.ones(len(spike_sublist)) * idx, marker='|', color=c)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.set_title(self.grid_labels[i])
                y_lims = ax.get_ylim()
                ax.set_yticks([y_lims[0], y_lims[1]/2, y_lims[1]])
                ax.set_yticklabels([y_labels[-1], y_labels[int(len(y_labels)/2)], 0])
                ax.set_ylabel('time of recording')
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
