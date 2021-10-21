from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
from numba import jit

from utility.channel_utility import ChannelUtility


class VoltageTraceHistogramPlot(QtWidgets.QWidget):
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
        # self.plot_widget.setLabel('left', 'amplitude [pA]', **styles)
        self.plot_widget.setLabel('bottom', 'count', **styles)
        main_layout.addWidget(self.plot_widget)

    @jit(forceobj=True)
    def scale_trace(self, trace_to_scale):
        vt = trace_to_scale
        conversion_factor = \
            self.mcs_reader.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['ConversionFactor']
        exponent = \
            self.mcs_reader.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['Exponent'] + 6
        # 6 = pV -> uV
        scaled_trace = vt * conversion_factor * np.power(10.0, exponent)
        return scaled_trace

    @jit(forceobj=True)
    def plot(self, label_index):
        self.plot_widget.clear()
        label = ChannelUtility.get_label_for_mcs_index(label_index, self.mcs_reader.channel_ids)
        self.label_index = ChannelUtility.get_sc_index(label_index, self.sc_reader.dead_channels)
        print('histogram plot:', label, '->', label_index)

        trace = self.sc_reader.base_file_voltage_traces[self.label_index]
        trace = self.scale_trace(trace)
        y, x = np.histogram(trace, bins=np.linspace(np.min(trace), np.max(trace), 80))
        bincenters = x[:-1] + np.diff(x)/2
        self.plot_widget.plot(y, bincenters[:-1], stepMode=True, fillLevel=0, fillOutline=True, brush='#006e7d')
        # hist.getViewBox().invertY(True)

