from PyQt5 import QtWidgets
import numpy as np
import pyqtgraph as pg
from numba import jit

from utility.channel_utility import ChannelUtility


class RawTraceWThresholdPlot(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, label, label_index):
        super().__init__(parent)
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.label = label
        self.label_index = label_index

        self.time = None
        self.base_file_trace = None
        self.scatter_mua_time = None
        self.scatter_mua_indices = None
        self.scatter_mua_amps = None

        self.scatter_cluster_time = None
        self.scatter_cluster_indices = None
        self.scatter_cluster_amps = None

        main_layout = QtWidgets.QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font-size': '10px'}
        self.plot_widget.setLabel('left', 'amplitude [pA]', **styles)
        self.plot_widget.setLabel('bottom', 'time [s]', **styles)
        self.pen_1 = pg.mkPen(color='#006e7d')

        self.dead_channels = self.sc_reader.dead_channels
        main_layout.addWidget(self.plot_widget)

    @jit(forceobj=True)
    def scale_trace(self, trace_to_scale):
        vt = trace_to_scale
        conversion_factor = \
            self.mcs_reader.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['ConversionFactor']
        exponent = self.mcs_reader.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['Exponent'] + 6
        # 6 = pV -> uV
        scaled_trace = vt * conversion_factor * np.power(10.0, exponent)
        return scaled_trace

    @jit(forceobj=True)
    def plot(self, label):
        self.plot_widget.clear()

        self.label_index = ChannelUtility.get_ordered_index(label)
        fs = self.mcs_reader.sampling_frequency

        # CAUTION: Filtering is now done by SC
        self.base_file_trace = self.sc_reader.base_file_voltage_traces[self.label_index]
        self.base_file_trace = self.scale_trace(self.base_file_trace)
        self.time = np.arange(0, len(self.base_file_trace) / fs, 1 / fs)

        self.plot_widget.plot(self.time, self.base_file_trace, pen=self.pen_1)
        if len(self.dead_channels) > 0:
            spike_index = ChannelUtility.get_sc_index(self.label_index, self.dead_channels)
            self.scatter_cluster_indices = self.sc_reader.spiketimes[spike_index]
            self.scatter_cluster_time = []
            self.scatter_cluster_amps = []
            for sj in sorted(self.scatter_cluster_indices):
                scatter_jdx = sj
                self.scatter_cluster_time.append(self.time[scatter_jdx])
                self.scatter_cluster_amps.append(self.base_file_trace[scatter_jdx])

        else:
            spike_index = self.channel_to_cluster_index[self.label_index]
            self.scatter_cluster_indices = self.sc_reader.spiketimes[spike_index]
            self.scatter_cluster_time = []
            self.scatter_cluster_amps = []
            for sj in sorted(self.scatter_cluster_indices):
                scatter_jdx = sj
                self.scatter_cluster_time.append(self.time[scatter_jdx])
                self.scatter_cluster_amps.append(self.base_file_trace[scatter_jdx])

        if len(self.dead_channels) > 0:
            if self.label_index not in self.dead_channels:
                self.plot_widget.plot(self.scatter_cluster_time, self.scatter_cluster_amps, pen=None, symbol='o',
                                      symbolPen=None, symbolSize=12)
                # ToDo: think about how to scatter current spike time
                self.plot_widget.plot(x=[self.scatter_cluster_time[0]], y=[self.scatter_cluster_amps[0]], pen=None,
                                      symbol='o', symbolPen=None, symbolSize=12, symbolBrush='r')

        else:
            self.plot_widget.plot(self.scatter_cluster_time, self.scatter_cluster_amps, pen=None, symbol='o',
                                  symbolPen=None, symbolSize=12)
            self.plot_widget.plot(x=[self.scatter_cluster_time[0]], y=[self.scatter_cluster_amps[0]],
                                  pen=None, symbol='o', symbolPen=None, symbolSize=12, symbolBrush='r')

    @jit(forceobj=True)
    def on_scatter_plot_updated(self, label_idx, index):
        self.plot_widget.clear()
        self.plot_widget.plot(self.time, self.base_file_trace, pen=self.pen_1)
        print(label_idx)
        if len(self.dead_channels) > 0:
            if label_idx not in self.dead_channels:
                self.plot_widget.plot(self.scatter_cluster_time, self.scatter_cluster_amps, pen=None, symbol='o',
                                      symbolPen=None, symbolSize=12)
                self.plot_widget.plot(x=[self.scatter_cluster_time[index]], y=[self.scatter_cluster_amps[index]],
                                      pen=None, symbol='o', symbolPen=None, symbolSize=12, symbolBrush='r')
        else:
            self.self.plot_widget.plot(self.scatter_cluster_time, self.scatter_cluster_amps, pen=None, symbol='o',
                                       symbolPen=None, symbolSize=12)
            self.plot_widget.plot(x=[self.scatter_cluster_time[index]], y=[self.scatter_cluster_amps[index]],
                                  pen=None, symbol='o', symbolPen=None, symbolSize=12, symbolBrush='r')
