from PyQt5 import QtWidgets
import numpy as np
import seaborn as sns
from scipy.signal import filtfilt, butter

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class VoltageTraceHistogramPlot(QtWidgets.QWidget):
    def __init__(self, parent, reader, label):
        # ToDo: probably get filtered (and whitened) traces in to 'see' what SC 'sees'
        super().__init__(parent)
        self.reader = reader
        self.label = label

        main_layout = QtWidgets.QVBoxLayout(self)

        plot_name = 'VT_Histogram_' + self.reader.filename + '_' + self.label
        plot_widget = PlotWidget(self, plot_name)
        self.figure = plot_widget.figure
        self.ax = self.figure.add_subplot(111)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()
        self.ax.tick_params(labelsize=10, direction='out')
        self.ax.set_xlabel(r'amplitude [$\mu$ V]')
        self.ax.set_ylabel('prevelance')
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
        self.ax.cla()
        self.ax.hist(filtered, density=True, bins=1000)
        self.figure.canvas.draw_idle()
