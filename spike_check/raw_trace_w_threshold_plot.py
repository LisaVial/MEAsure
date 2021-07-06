from PyQt5 import QtWidgets
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.gridspec as gridspec

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
        self.base_file_trace = None
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
        gs = gridspec.GridSpec(1, 3, wspace=0, hspace=.5)
        sns.set()

        self.ax_preproc = self.figure.add_subplot(gs[0, :2])
        self.ax_preproc.spines['right'].set_visible(False)
        self.ax_preproc.spines['top'].set_visible(False)
        self.ax_preproc.get_xaxis().tick_bottom()
        self.ax_preproc.get_yaxis().tick_left()
        self.ax_preproc.tick_params(labelsize=10, direction='out')
        self.ax_preproc.set_xlabel('time [sec]')
        self.ax_preproc.set_ylabel(r'voltage [$\mu$ V]')

        self.ax_hist = self.figure.add_subplot(gs[0, 2])

        self.dead_channels = self.sc_reader.dead_channels
        self.cluster_to_channel_index = dict()
        self.channel_to_cluster_index = dict()  # note: dead channels do not have a cluster

        cluster_index = 0
        for channel_index in range(ChannelUtility.get_label_count()):
            if len(self.dead_channels) > 0:
                if channel_index not in self.dead_channels:
                    self.cluster_to_channel_index[cluster_index] = channel_index
                    self.channel_to_cluster_index[channel_index] = cluster_index
                    cluster_index += 1  # increase cluster index
            else:
                self.cluster_to_channel_index[cluster_index] = channel_index
                self.channel_to_cluster_index[channel_index] = cluster_index
                cluster_index += 1  # increase cluster index

        main_layout.addWidget(plot_widget)

    def scale_trace(self, trace_to_scale):
        vt = trace_to_scale
        conversion_factor = \
            self.mcs_reader.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['ConversionFactor']
        exponent = self.mcs_reader.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['Exponent'] + 6
        # 6 = pV -> uV
        scaled_trace = vt * conversion_factor * np.power(10.0, exponent)
        return scaled_trace

    def plot(self, label):
        # self.label_index = ChannelUtility.get_ordered_index(label)
        fs = self.mcs_reader.sampling_frequency

        # CAUTION: Filtering is now done by SC
        self.filter_trace = self.mcs_reader.get_scaled_channel(label)
        self.base_file_trace = self.sc_reader.base_file_voltage_traces[self.label_index]
        self.base_file_trace = self.scale_trace(self.base_file_trace)
        self.time = np.arange(0, len(self.filter_trace) / fs, 1 / fs)

        if len(self.dead_channels) > 0:
            if self.label_index not in self.dead_channels:
                self.scatter_mua_indices, sorted_mua_amplitudes = self.sc_reader.retrieve_mua_spikes()
                spike_index = self.channel_to_cluster_index[self.label_index]
                self.scatter_mua_time = self.scatter_mua_indices[spike_index] / fs
                self.scatter_mua_amps = [self.filter_trace[idx] for idx in self.scatter_mua_indices[spike_index]]

            if self.label_index not in self.dead_channels:
                spike_index = self.channel_to_cluster_index[self.label_index]
                self.scatter_cluster_indices = self.sc_reader.spiketimes[spike_index]
                self.scatter_cluster_time = []
                self.scatter_cluster_amps = []
                for sj in sorted(self.scatter_cluster_indices):
                    scatter_jdx = sj
                    try:
                        self.scatter_cluster_time.append(self.time[scatter_jdx])
                        self.scatter_cluster_amps.append(self.base_file_trace[scatter_jdx])
                    except IndexError:
                        scatter_t_max_jdx = min(scatter_jdx, len(self.time) - 1)
                        self.scatter_cluster_time.append(self.time[scatter_t_max_jdx])
                        self.scatter_cluster_amps.append(self.base_file_trace[scatter_t_max_jdx])
        else:
            self.scatter_mua_indices, sorted_mua_amplitudes = self.sc_reader.retrieve_mua_spikes()
            spike_index = self.channel_to_cluster_index[self.label_index]
            self.scatter_mua_time = self.scatter_mua_indices[spike_index] / fs
            self.scatter_mua_amps = [self.filter_trace[idx] for idx in self.scatter_mua_indices[spike_index]]
            # spike_index = self.channel_to_cluster_index[self.label_index]
            self.scatter_cluster_indices = self.sc_reader.spiketimes[spike_index]
            self.scatter_cluster_time = []
            self.scatter_cluster_amps = []
            for sj in sorted(self.scatter_cluster_indices):
                scatter_jdx = sj
                try:
                    self.scatter_cluster_time.append(self.time[scatter_jdx])
                    self.scatter_cluster_amps.append(self.base_file_trace[scatter_jdx])
                except IndexError:
                    scatter_t_max_jdx = min(scatter_jdx, len(self.time) - 1)
                    self.scatter_cluster_time.append(self.time[scatter_t_max_jdx])
                    self.scatter_cluster_amps.append(self.base_file_trace[scatter_t_max_jdx])

        self.ax_preproc.cla()
        self.ax_preproc.plot(self.time, self.base_file_trace, zorder=1)
        if len(self.dead_channels) > 0:
            if self.label_index not in self.dead_channels:
                self.ax_preproc.scatter(self.scatter_cluster_time, self.scatter_cluster_amps, marker='o', color='k',
                                        zorder=2)
                self.ax_preproc.scatter(self.scatter_cluster_time[0], self.scatter_cluster_amps[0], marker='o',
                                        color='red',
                                        zorder=2)
                self.ax_preproc.set_xlabel('time [s]')
                self.ax_preproc.set_ylabel(r'voltage [$\mu\,$V]')
        else:
            self.ax_preproc.scatter(self.scatter_cluster_time, self.scatter_cluster_amps, marker='o', color='k',
                                    zorder=2)
            self.ax_preproc.scatter(self.scatter_cluster_time[0], self.scatter_cluster_amps[0], marker='o', color='red',
                                    zorder=2)
            self.ax_preproc.set_xlabel('time [s]')
            self.ax_preproc.set_ylabel(r'voltage [$\mu\,$V]')
        trace = self.base_file_trace
        self.ax_hist.cla()
        vert_hist = np.histogram(trace, bins=1000)
        height = np.ceil(max(vert_hist[1])) - np.floor(min(vert_hist[1]))
        height = height / len(vert_hist[0])
        self.ax_hist.barh(vert_hist[1][:-1], vert_hist[0], height=height)
        self.ax_hist.get_xaxis().set_visible(False)
        self.ax_hist.get_yaxis().set_visible(False)
        self.figure.canvas.draw_idle()

    def on_scatter_plot_updated(self, label_idx, index):
        self.ax_preproc.cla()
        self.ax_preproc.grid(False)
        self.ax_preproc.plot(self.time, self.base_file_trace, zorder=1)
        print(label_idx)
        if len(self.dead_channels) > 0:
            if label_idx not in self.dead_channels:
                self.ax_preproc.scatter(self.scatter_cluster_time, self.scatter_cluster_amps, marker='o', color='k',
                                        zorder=2)
                self.ax_preproc.scatter(self.scatter_cluster_time[index], self.scatter_cluster_amps[index], marker='o',
                                        color='red', zorder=2)
                self.ax_preproc.set_xlabel('time [s]')
                self.ax_preproc.set_ylabel(r'voltage [$\mu\,$V]')
        else:
            self.ax_preproc.scatter(self.scatter_cluster_time, self.scatter_cluster_amps, marker='o', color='k',
                                    zorder=2)
            self.ax_preproc.scatter(self.scatter_cluster_time[index], self.scatter_cluster_amps[index], marker='o',
                                    color='red', zorder=2)
            self.ax_preproc.set_xlabel('time [s]')
            self.ax_preproc.set_ylabel(r'voltage [$\mu\,$V]')

        self.figure.canvas.draw_idle()
