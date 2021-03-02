from PyQt5 import QtCore, QtWidgets
import numpy as np
import seaborn as sns
from scipy.signal import filtfilt, butter
from scipy.stats import median_absolute_deviation

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class RawTraceWThresholdPlot(QtWidgets.QWidget):
    def __init__(self, parent, reader, label):
        super().__init__(parent)
        self.reader = reader
        self.label = label
        main_layout = QtWidgets.QVBoxLayout(self)

        plot_name = 'SpikeVerification_RawTracewThreshold_' + self.reader.filename + '_' + self.label

        plot_widget = PlotWidget(self, plot_name)
        self.figure = plot_widget.figure
        sns.set()
        self.ax = self.figure.add_subplot(111)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()
        self.ax.tick_params(labelsize=10, direction='out')
        self.ax.set_xlabel('time [sec]')
        self.ax.set_ylabel(r'voltage [$\mu$ V]')
        self.plot(self.label)

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

    def plot(self, label):
        scaled_trace = self.reader.get_scaled_channel(label)
        fs = self.reader.sampling_frequency
        filtered = self.butter_bandpass_filter(scaled_trace[10000:], 300, 4750, fs)
        mad = median_absolute_deviation(filtered)
        time = np.arange(0, len(filtered)/fs, 1/fs)
        # ToDo: what to do about substracting the median?
        self.ax.cla()
        self.ax.plot(time, filtered)
        self.ax.hlines(-6 * mad, 0, time[-1])
        self.figure.canvas.draw_idle()
