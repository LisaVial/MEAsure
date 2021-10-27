from PyQt5 import QtWidgets
import numpy as np
import pyqtgraph as pg
from numba import jit

from utility.channel_utility import ChannelUtility


class SpikeTimePlot(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, label, label_index):
        super().__init__(parent)
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.label = label
        self.label_index = label_index

        main_layout = QtWidgets.QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font-size': '10px'}
        self.plot_widget.setLabel('left', 'amplitude [pA]', **styles)
        self.plot_widget.setLabel('bottom', 'time [s]', **styles)

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
    def plot(self, label_index, spike_idx):
        self.plot_widget.clear()
        self.label_index = label_index
        spike_index = ChannelUtility.get_sc_index(label_index, self.dead_channels)
        label = ChannelUtility.get_label_for_mcs_index(label_index, self.mcs_reader.channel_ids)
        print('spike time plot:', label, '->', self.label_index)

        trace = self.sc_reader.base_file_voltage_traces[label_index]
        trace = self.scale_trace(trace)
        fs = self.mcs_reader.sampling_frequency

        spiketime_index = self.sc_reader.spiketimes[spike_index][spike_idx]

        spiketime = spiketime_index/fs
        st_start_index = max(int(spiketime_index - 500), 0)   # entspricht 50 ms
        st_end_index = min(int((spiketime_index + 500)+1), len(trace))
        time = np.arange((st_start_index/fs), (st_end_index/fs), 1/fs)
        if len(time) < len(trace[st_start_index:st_end_index]):
            time = np.arange((st_start_index / fs), (st_end_index / fs) + 1 / fs, 1 / fs)
        elif len(time) > len(trace[st_start_index:st_end_index]):
            time = time[:len(trace[st_start_index:st_end_index])]
        if len(self.dead_channels) > 0:
            if label_index not in self.dead_channels:
                self.plot_widget.plot(time, trace[st_start_index:st_end_index],
                                      pen='#006e7d')
                if spiketime_index < len(trace):
                    self.plot_widget.plot(x=[spiketime], y=[trace[spiketime_index]], pen=None, symbol='o',
                                          symbolPen=None, symbolSize=12, symbolBrush='r')
        else:
            self.plot_widget.plot(time, trace[st_start_index:st_end_index], pen='#006e7d')
            if spiketime_index < len(trace):
                self.plot_widget.plot(x=[spiketime], y=[trace[spiketime_index]], pen=None, symbol='o', symbolPen=None,
                                      symbolSize=12, symbolBrush='r')
