from PyQt5 import QtWidgets, QtCore
import numpy as np
from scipy.signal import filtfilt, butter, find_peaks, peak_prominences
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from IPython import embed

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class CsdPlotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_channel_indices, grid_labels, fs, settings):
        # sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
        super().__init__(parent)
        self.reader = reader
        self.grid_channel_indices = grid_channel_indices
        self.grid_labels = grid_labels
        self.fs = fs
        self.settings = settings

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        file_name = self.reader.filename
        plot_name = 'CSD_Plot_' + file_name

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)

        self.ch_ids = self.reader.channel_ids
        self.labels = self.reader.labels
        self.fs = self.reader.sampling_frequency
        self.duration = self.reader.current_file['duration']

        self.plot(self.figure)

    def plot(self, figure):
        time = np.arange(0, self.reader.voltage_traces_dataset.shape[1]/self.fs, 1/self.fs)

        big_proms = []
        channel_order = []
        filtered = []
        for idx, label in enumerate(self.grid_labels):
            signal = self.reader.get_traces_with_label(label)
            fs = self.reader.sampling_frequency

            nyq = 0.5 * fs
            normal_cutoff = 10 / nyq
            b, a = butter(2, normal_cutoff, btype='low', analog=False)
            y = filtfilt(b, a, signal)

            peaks, _ = find_peaks(y, threshold=(5*np.mean(y)))
            proms, left_bases, right_bases = peak_prominences(y, peaks)
            if 200 < proms[0] < 500:
                filtered.append(y)
                big_proms.append(proms[0])
                channel_order.append(idx)

        spec = gridspec.GridSpec(ncols=1, nrows=len(big_proms), figure=figure)
        cNorm = colors.Normalize(vmin=0, vmax=len(big_proms))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap='bone')
        for i, prom_idx in enumerate(reversed(np.argsort(big_proms))):
            colorVal = scalarMap.to_rgba(filtered[prom_idx][10000:100001])
            ax = figure.add_subplot(spec[i])
            ax.plot(time[10000:100001], filtered[prom_idx][10000:100001], color='white')
            ax.fill_between(time[10000:100001], np.zeros(len(filtered[prom_idx][10000:100001])),
                              filtered[prom_idx][10000:100001], alpha=0.75, color=colorVal)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            # ax.get_xaxis().tick_bottom()
            # ax.get_yaxis().tick_left()
            ax.tick_params(labelsize=10, direction='out')


    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
