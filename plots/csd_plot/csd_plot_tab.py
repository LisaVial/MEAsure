from PyQt5 import QtWidgets, QtCore
import numpy as np
from scipy.signal import filtfilt, butter, find_peaks, peak_prominences
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.pylab as pl
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

        maxima = []
        filtered = []
        labels = []
        for idx, label in enumerate(self.grid_labels):
            if len(label) > 2:
                continue
            signal = self.reader.get_traces_with_label(label)
            # function to scale voltage trace
            fs = self.reader.sampling_frequency

            nyq = 0.5 * fs
            normal_cutoff = 10 / nyq
            b, a = butter(2, normal_cutoff, btype='low', analog=False)
            y = filtfilt(b, a, signal)
            max = np.argmax(y)
            max_timepoint = max/fs
            print('Maxima timepoint:', max/fs, '\n', 'and their respective values:', signal[max])
            if max_timepoint > 5 and signal[max] > 50 or signal[max] < -50:
                filtered.append(y)
                labels.append(label)
                maxima.append(max)

        spec = gridspec.GridSpec(ncols=1, nrows=len(filtered[:5]), figure=figure)
        colors = plt.cm.tab20b(np.linspace(0, 1, len(filtered[:5])))
        axs_objs = []
        sorted_maxima = np.array(maxima)[np.argsort(maxima)]
        for i, maxi in enumerate(sorted_maxima[:5]):
            max_index = len(filtered[i])
            if maxi > 5000:
                start_index = maxi - 5000
                end_index = min((maxi + 5000), max_index)
            else:
                start_index = 0
                end_index = min((maxi + 10000), max_index)
            ax = figure.add_subplot(spec[i])
            # ax.plot(time[start_index:end_index], filtered[i][start_index:end_index], color='white')
            ax.fill_between(time[start_index:end_index], np.zeros(len(filtered[i][start_index:end_index])),
                            filtered[i][start_index:end_index], color=colors[i])
            ax.text(1.5, 0.9, str(labels[i]), color=colors[i])
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            # ax.spines['left'].set_visible(False)
            # ax.spines['bottom'].set_visible(False)
            # ax.axes.get_xaxis().set_visible(False)
            # ax.axes.get_yaxis().set_visible(False)
            # ax.axes.get_xaxis().set_ticks([])
            # ax.axes.get_yaxis().set_ticks([])
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

    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
