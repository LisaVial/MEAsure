from PyQt5 import QtWidgets, QtCore
import numpy as np
from scipy.signal import filtfilt, butter, find_peaks, peak_prominences
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from IPython import embed

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class CsdPlotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_channel_indices, grid_labels, fs, settings):
        super().__init__(parent)
        sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
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
        labels = []
        for idx, label in enumerate(self.grid_labels):
            signal = self.reader.get_traces_with_label(label)
            fs = self.reader.sampling_frequency

            nyq = 0.5 * fs
            normal_cutoff = 10 / nyq
            b, a = butter(2, normal_cutoff, btype='low', analog=False)
            y = filtfilt(b, a, signal)

            peaks, _ = find_peaks(y[:100001], threshold=(2.5*np.mean(y[:100001])))
            proms = peak_prominences(y[:100001], peaks)
            for pi, prom in enumerate(proms):
                for p in prom:
                    if 1000 < p < 1500:
                        filtered.append(y[:100001])
                        big_proms.append(p)
                        break

        spec = gridspec.GridSpec(ncols=1, nrows=len(big_proms), figure=figure)
        cNorm = colors.Normalize(vmin=0, vmax=len(big_proms))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap='bone')
        axs_objs = []
        for i, prom_idx in enumerate(np.argsort(big_proms)):
            colorVal = scalarMap.to_rgba(filtered[prom_idx])
            ax = figure.add_subplot(spec[i])
            ax.plot(time[:100001], filtered[prom_idx], color='white')
            ax.fill_between(time[:100001], np.zeros(len(filtered[prom_idx])), filtered[prom_idx], alpha=0.75,
                            color=colorVal)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)
            ax.axes.get_xaxis().set_ticks([])
            ax.axes.get_yaxis().set_ticks([])
            ax.tick_params(labelsize=10, direction='out')
            axs_objs.append(ax)
        spec.update(hspace=-0.5)
        rect = axs_objs[-1].patch
        rect.set_alpha(0)

        # Define and use a simple function to label the plot in axes coordinates
        def label(x, color, label):
            ax = plt.gca()
            ax.text(0, .2, label, fontweight="bold", color=color,
                    ha="left", va="center", transform=ax.transAxes)

        g.map(label, "x")

        # Set the subplots to overlap
        g.fig.subplots_adjust(hspace=-.25)

        # Remove axes details that don't play well with overlap
        g.set_titles("")
        g.set(yticks=[])
        g.despine(bottom=True, left=True)

    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
