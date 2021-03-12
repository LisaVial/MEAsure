from PyQt5 import QtWidgets
import numpy as np
import seaborn as sns
from scipy.signal import filtfilt, butter

from plot_manager import PlotManager
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

        main_layout.addWidget(plot_widget)

    def butter_bandpass(self, lowcut, highcut, fs, order=3):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=3):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    def plot(self, channel_idx, idx):
        trace = self.mcs_reader.voltage_traces[channel_idx]
        fs = self.mcs_reader.sampling_frequency

        spiketime_index = self.sc_reader.spiketimes[channel_idx][idx]

        spiketime = spiketime_index/fs
        st_start_index = max(int(spiketime_index - 50), 0)   # entspricht 5 ms
        st_end_index = min(int(spiketime_index + 50), len(trace))
        time = np.arange((st_start_index/fs), (st_end_index/fs), 1/fs)
        self.ax.cla()
        try:
            self.ax.plot(time, trace[st_start_index:st_end_index])
        except ValueError:
            self.ax.plot(time[:-1], trace[st_start_index:st_end_index])
        if spiketime_index < len(trace):
            self.ax.scatter(spiketime, trace[spiketime_index], marker='o', color='red', zorder=2)
        self.figure.canvas.draw_idle()