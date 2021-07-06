from PyQt5 import QtWidgets
import numpy as np
import seaborn as sns
import matplotlib as mpl
from IPython import embed

from plots.plot_widget import PlotWidget
from utility.channel_utility import ChannelUtility


class SpikeSortingPlot(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, label):
        super().__init__(parent)
        mpl.rcParams['agg.path.chunksize'] = 10000
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.label = label

        main_layout = QtWidgets.QVBoxLayout(self)
        plot_name = 'SpikeSortingAmplitudes_' + self.mcs_reader.filename + '_' + self.label

        plot_widget = PlotWidget(self, plot_name)
        self.figure = plot_widget.figure
        sns.set()
        self.ax = self.figure.add_subplot(111)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()

        self.dead_channels = self.sc_reader.dead_channels
        # self.dead_channels = [0, 1, 14, 15, 30, 31, 190, 206, 222]
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

    def plot(self, label, st_index):
        label_index = ChannelUtility.get_ordered_index(label)
        if len(self.dead_channels) > 0:
            if label_index not in self.dead_channels:
                self.ax.cla()
                fs = self.mcs_reader.sampling_frequency

                trace = self.mcs_reader.voltage_traces[label_index]

                step_index = 0.002 * fs
                spike_index = self.channel_to_cluster_index[label_index]
                spike_indices = self.sc_reader.spiketimes[spike_index]
                spike_amplitudes = []
                for spike_index in spike_indices:
                    spike_min_idx = int(max(0, spike_index - step_index))
                    spike_max_idx = int(min(spike_index + step_index, len(trace)))
                    spike_vt = trace[spike_min_idx:spike_max_idx]
                    spike_amplitudes.append(spike_vt)
                    spike_time = np.arange(-0.002, 0.002, 1/fs)
                    for i, spike_amp in enumerate(spike_amplitudes):
                        spike_amp = spike_amp - spike_amp[0]
                        if i == st_index:
                            self.ax.plot(spike_time, spike_amp, color='r', zorder=2)
                            self.ax.set_xticklabels([])
                            self.ax.set_yticklabels([])
                        else:
                            self.ax.plot(spike_time, spike_amp, color='k', zorder=1)
                            self.ax.set_xticklabels([])
                            self.ax.set_yticklabels([])
                        self.figure.canvas.draw_idle()
        else:
            self.ax.cla()
            fs = self.mcs_reader.sampling_frequency

            trace = self.mcs_reader.voltage_traces[label_index]

            step_index = 0.002 * fs
            spike_index = self.channel_to_cluster_index[label_index]
            spike_indices = self.sc_reader.spiketimes[spike_index]
            spike_amplitudes = []
            for spike_index in spike_indices:
                spike_min_idx = int(max(0, spike_index - step_index))
                spike_max_idx = int(min(spike_index + step_index, len(trace)))
                spike_vt = trace[spike_min_idx:spike_max_idx]
                spike_amplitudes.append(spike_vt)
                spike_time = np.arange(-0.002, 0.002, 1 / fs)
                for i, spike_amp in enumerate(spike_amplitudes):
                    spike_amp = spike_amp - spike_amp[0]
                    if i == st_index:
                        self.ax.plot(spike_time, spike_amp, color='r', zorder=2)
                        self.ax.set_xticklabels([])
                        self.ax.set_yticklabels([])
                    else:
                        self.ax.plot(spike_time, spike_amp, color='k', zorder=1)
                        self.ax.set_xticklabels([])
                        self.ax.set_yticklabels([])
                    self.figure.canvas.draw_idle()