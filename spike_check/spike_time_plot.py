from PyQt5 import QtWidgets
import numpy as np
import seaborn as sns

from plot_manager import PlotManager
from utility.channel_utility import ChannelUtility
from plots.plot_widget import PlotWidget


class SpikeTimePlot(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, label, label_index):
        super().__init__(parent)
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.label = label
        self.label_index = label_index

        main_layout = QtWidgets.QVBoxLayout(self)

        plot_name = 'SpikeTimePlot_' + self.mcs_reader.filename + '_' + self.label

        plot_widget = PlotWidget(self, plot_name)
        sns.set()
        self.figure = plot_widget.figure
        self.ax = self.figure.add_subplot(111)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()
        self.ax.tick_params(labelsize=10, direction='out')
        self.ax.set_xlabel('time [msec]')
        self.ax.set_ylabel(r'voltage [$\mu$ V]')

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

        main_layout.addWidget(plot_widget)

    def plot(self, label_index, spike_idx):
        if len(self.dead_channels) > 0:
            if label_index not in self.dead_channels:
                spike_label_index = self.channel_to_cluster_index[label_index]
            else:
                spike_label_index = label_index
        else:
            spike_label_index = label_index
        trace = self.sc_reader.base_file_voltage_traces[label_index]
        fs = self.mcs_reader.sampling_frequency

        spiketime_index = self.sc_reader.spiketimes[spike_label_index][spike_idx]

        spiketime = spiketime_index/fs
        st_start_index = max(int(spiketime_index - 500), 0)   # entspricht 50 ms
        st_end_index = min(int(spiketime_index + 500), len(trace))
        time = np.arange((st_start_index/fs), (st_end_index/fs), 1/fs)
        if len(self.dead_channels) > 0:
            if label_index not in self.dead_channels:
                self.ax.cla()
                self.ax.set_xticklabels([])
                self.ax.set_yticklabels([])
                try:
                    self.ax.plot(time, trace[st_start_index:st_end_index])
                except ValueError:
                    self.ax.plot(time[:-1], trace[st_start_index:st_end_index])
                if spiketime_index < len(trace):
                    self.ax.scatter(spiketime, trace[spiketime_index], marker='o', color='red', zorder=2)
                    self.ax.set_xticklabels([])
                    self.ax.set_yticklabels([])
                self.figure.canvas.draw_idle()
        else:
            self.ax.cla()
            try:
                self.ax.plot(time, trace[st_start_index:st_end_index])
            except ValueError:
                self.ax.plot(time[:-1], trace[st_start_index:st_end_index])
            self.ax.set_xticklabels([])
            self.ax.set_yticklabels([])
            if spiketime_index < len(trace):
                self.ax.scatter(spiketime, trace[spiketime_index], marker='o', color='red', zorder=2)
                self.ax.set_xticklabels([])
                self.ax.set_yticklabels([])
            self.figure.canvas.draw_idle()
