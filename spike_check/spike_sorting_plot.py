from PyQt5 import QtWidgets
import numpy as np
import pyqtgraph as pg
from numba import jit

from utility.channel_utility import ChannelUtility


class SpikeSortingPlot(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, label):
        super().__init__(parent)
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.label = label

        main_layout = QtWidgets.QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font-size': '10px'}
        self.plot_widget.setLabel('left', 'amplitude [pA]', **styles)
        self.plot_widget.setLabel('bottom', 'time [s]', **styles)
        self.pen_1 = pg.mkPen(color='#006e7d')
        self.pen_2 = pg.mkPen(color='r')

        self.dead_channels = self.sc_reader.dead_channels

        main_layout.addWidget(self.plot_widget)

    @jit(forceobj=True)
    def plot(self, label, st_index):
        self.plot_widget.clear()
        label_index = ChannelUtility.get_ordered_index(label)
        spike_index = ChannelUtility.get_sc_index(label_index, self.dead_channels)
        print('Spike sorting plot:', label, '->', label_index)
        if len(self.dead_channels) > 0:
            if label_index not in self.dead_channels:

                fs = self.mcs_reader.sampling_frequency

                trace = self.mcs_reader.voltage_traces[label_index]
                # ToDo: correct code so there is no shadow of variable names
                step_index = 0.002 * fs
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
                            self.plot_widget.plot(spike_time, spike_amp, pen=self.pen_2)
                        else:
                            self.plot_widget.plot(spike_time, spike_amp, pen=self.pen_1)
        else:
            fs = self.mcs_reader.sampling_frequency

            trace = self.mcs_reader.voltage_traces[label_index]

            step_index = 0.002 * fs
            spike_index = ChannelUtility.get_sc_index(label_index, self.dead_channels)
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
                        self.plot_widget.plot(spike_time, spike_amp, pen=self.pen_2)
                    else:
                        self.plot_widget.plot(spike_time, spike_amp, pen=self.pen_1)
