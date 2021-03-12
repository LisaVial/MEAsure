from PyQt5 import QtCore, QtWidgets
import numpy as np
import seaborn as sns
from scipy.signal import filtfilt, butter
from scipy.stats import median_absolute_deviation
import matplotlib as mpl
from IPython import embed

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget
from utility.channel_utility import ChannelUtility


class RawTraceWThresholdPlot(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, label, label_index):
        super().__init__(parent)
        mpl.rcParams['agg.path.chunksize'] = 10000
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.label = label
        self.label_index = label_index

        self.time = None
        self.filter_trace = None
        self.preproc_trace = None
        self.scatter_mua_time = None
        self.scatter_mua_indices = None
        self.scatter_mua_amps = None

        self.scatter_cluster_time = None
        self.scatter_cluster_indices = None
        self.scatter_cluster_amps = None

        main_layout = QtWidgets.QVBoxLayout(self)

        plot_name = 'SpikeVerification_RawTracewThreshold_' + self.mcs_reader.filename + '_' + self.label

        plot_widget = PlotWidget(self, plot_name)
        self.figure = plot_widget.figure
        sns.set()
        self.ax_raw = self.figure.add_subplot(211)
        self.ax_raw.spines['right'].set_visible(False)
        self.ax_raw.spines['top'].set_visible(False)
        self.ax_raw.get_xaxis().tick_bottom()
        self.ax_raw.get_yaxis().tick_left()
        self.ax_raw.tick_params(labelsize=10, direction='out')
        # self.ax_raw.set_xlabel('time [sec]')
        # self.ax_raw.set_ylabel(r'voltage [$\mu$ V]')

        # self.ax_mua_scatter = self.ax_raw.twinx()
        # self.ax_mua_scatter.spines['right'].set_visible(False)
        # self.ax_mua_scatter.spines['top'].set_visible(False)
        # self.ax_mua_scatter.spines['left'].set_visible(False)
        # self.ax_mua_scatter.spines['bottom'].set_visible(False)
        # self.ax_mua_scatter.grid(False)

        self.ax_preproc = self.figure.add_subplot(212)
        self.ax_preproc.spines['right'].set_visible(False)
        self.ax_preproc.spines['top'].set_visible(False)
        self.ax_preproc.get_xaxis().tick_bottom()
        self.ax_preproc.get_yaxis().tick_left()
        self.ax_preproc.tick_params(labelsize=10, direction='out')
        self.ax_preproc.set_xlabel('time [sec]')
        self.ax_preproc.set_ylabel(r'voltage [$\mu$ V]')

        # self.ax_cluster_scatter = self.ax_preproc.twinx()
        # self.ax_cluster_scatter.spines['right'].set_visible(False)
        # self.ax_cluster_scatter.spines['top'].set_visible(False)
        # self.ax_cluster_scatter.spines['left'].set_visible(False)
        # self.ax_cluster_scatter.spines['bottom'].set_visible(False)
        # self.ax_cluster_scatter.grid(False)
        main_layout.addWidget(plot_widget)

    def butter_bandpass(self, lowcut, highcut, fs, order=3):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='pass')
        return b, a

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=3):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = filtfilt(b, a, data, axis=0)
        return y

    def plot(self, label):
        thresholds = self.sc_reader.retrieve_thresholds()
        self.label_index = ChannelUtility.get_ordered_index(label)
        # self.filter_trace = filter_mat[self.label_index]
        fs = self.mcs_reader.sampling_frequency

        # CAUTION: Filtering is now done by SC
        self.filter_trace = self.mcs_reader.voltage_traces[self.label_index]
        self.time = np.arange(0, len(self.filter_trace)/fs, 1/fs)

        self.scatter_mua_indices, sorted_mua_amplitudes = self.sc_reader.retrieve_mua_spikes()
        self.scatter_mua_time = [st/fs for st in self.scatter_mua_indices]
        self.scatter_mua_amps = sorted_mua_amplitudes
        # for si in sorted(self.scatter_mua_indices[self.label_index]):
        #     scatter_idx = si
        #     try:
        #         self.scatter_mua_time.append(self.time[scatter_idx])
        #         self.scatter_mua_amps.append(self.filter_trace[scatter_idx])
        #     except IndexError:
        #         scatter_t_max_idx = min(scatter_idx, len(self.filter_trace)-1)
        #         self.scatter_mua_time.append(self.time[scatter_t_max_idx])
        #         self.scatter_mua_amps.append(self.filter_trace[scatter_t_max_idx])

        self.scatter_cluster_indices = self.sc_reader.spiketimes[self.label_index]
        self.scatter_cluster_time = []
        self.scatter_cluster_amps = []
        for sj in sorted(self.scatter_cluster_indices):
            scatter_jdx = sj
            try:
                self.scatter_cluster_time.append(self.time[scatter_jdx])
                self.scatter_cluster_amps.append(self.filter_trace[scatter_jdx])
            except IndexError:
                scatter_t_max_jdx = min(scatter_jdx, len(self.time) - 1)
                self.scatter_cluster_time.append(self.time[scatter_t_max_jdx])
                self.scatter_cluster_amps.append(self.filter_trace[scatter_t_max_jdx])

        self.ax_raw.cla()
        self.ax_raw.plot(self.time, self.filter_trace, zorder=1)

        self.ax_raw.scatter(self.scatter_mua_time[self.label_index], self.scatter_mua_amps[self.label_index],
                            marker='o', color='k', zorder=2)
        self.ax_raw.hlines(-thresholds[self.label_index], 0, self.time[-1], color='r', zorder=2)

        self.ax_preproc.cla()
        # embed()
        self.preproc_trace = self.filter_trace
        self.ax_preproc.plot(self.time, self.preproc_trace, zorder=1)

        self.ax_preproc.scatter(self.scatter_cluster_time, self.scatter_cluster_amps, marker='o', color='k', zorder=2)
        self.ax_preproc.scatter(self.scatter_cluster_time[0], self.scatter_cluster_amps[0], marker='o', color='red',
                                zorder=2)
        # self.ax_preproc.hlines(thresholds[self.label_index], 0, self.time[-1], color='r', zorder=2)
        self.figure.canvas.draw_idle()

    def on_scatter_plot_updated(self, index):
        self.ax_preproc.cla()
        self.ax_preproc.grid(False)
        self.ax_preproc.plot(self.time, self.preproc_trace, zorder=1)
        self.ax_preproc.scatter(self.scatter_cluster_time, self.scatter_cluster_amps, marker='o', color='k', zorder=2)
        self.ax_preproc.scatter(self.scatter_cluster_time[index], self.scatter_cluster_amps[index], marker='o',
                                color='red', zorder=2)
        self.figure.canvas.draw_idle()
