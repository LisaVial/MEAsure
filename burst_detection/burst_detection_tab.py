from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np

from burst_detection.burst_detection_thread import BurstDetectionThread
from utility.channel_utility import ChannelUtility


class BurstDetectionTab(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, grid_labels, grid_indices, settings):
        super().__init__(parent)
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.sc_filter_traces = self.sc_reader.base_file_voltage_traces
        self.grid_indices = grid_indices
        self.grid_labels = grid_labels
        self.settings = settings

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        operation_layout = QtWidgets.QVBoxLayout(self)
        operation_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far...')
        operation_layout.addWidget(self.operation_label)

        self.progress_label = QtWidgets.QLabel(self)
        operation_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setVisible(True)
        operation_layout.addWidget(self.progress_bar)
        main_layout.addLayout(operation_layout)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font size': '10 px'}
        self.plot_widget.setLabel('left', 'amplitude', units='<font>&mu;V</font>', **styles)
        self.plot_widget.setLabel('bottom', 'time', units='s', **styles)
        main_layout.addWidget(self.plot_widget)

        self.scatter_plot = None

        self.burst_detection_thread = None
        self.all_bursts = None

    def scale_trace(self, trace_to_scale):
        vt = trace_to_scale
        conversion_factor = \
            self.mcs_reader.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['ConversionFactor']
        exponent = self.mcs_reader.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['Exponent'] + 6
        # 6 = pV -> uV
        scaled_trace = vt * conversion_factor * np.power(10.0, exponent)
        return scaled_trace

    def initialize_burst_detection(self):
        if self.burst_detection_thread is None:
            self.progress_bar.setValue(0)
            self.operation_label.setText('Initializing burst detection.')
            self.burst_detection_thread = BurstDetectionThread(self, self.sc_reader.spiketimes, self.grid_labels,
                                                               self.grid_indices, self.mcs_reader.sampling_frequency,
                                                               self.settings)
            self.burst_detection_thread.progress_made.connect(self.on_progress_made)
            self.burst_detection_thread.operation_changed.connect(self.on_operation_changed)
            self.burst_detection_thread.data_updated.connect(self.on_data_updated)
            self.burst_detection_thread.finished.connect(self.on_burst_detection_thread_finished)
            debug_mode = False
            if debug_mode:
                self.burst_detection_thread.run()
            else:
                self.burst_detection_thread.start()

    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + '%')

    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    def on_data_updated(self, data):
        # every time a channel has been analyzed the data necessary to create a plot will be sent here
        label = data[0]
        mcs_idx = data[1]
        burst_indices = data[2]
        self.plot_widget.clear()
        if len(burst_indices) > 0:
            text = 'channel ' + str(label)
            mssg = pg.TextItem(text)
            self.plot_widget.addItem(mssg)
            dead_channels = self.sc_reader.dead_channels
            sc_index = ChannelUtility.get_sc_index(mcs_idx, dead_channels)
            raw_signal = self.sc_filter_traces[sc_index]
            start_time = int(burst_indices[0] - (0.1*self.mcs_reader.sampling_frequency))
            start_time = max(0, start_time)
            end_time = int(burst_indices[-1] + (0.1*self.mcs_reader.sampling_frequency))
            end_time = min(len(raw_signal), end_time)
            plot_signal = raw_signal[start_time:end_time]
            plot_time = np.arange(start_time/self.mcs_reader.sampling_frequency,
                                  end_time/self.mcs_reader.sampling_frequency, 1/self.mcs_reader.sampling_frequency)
            scatter_amps = [raw_signal[burst_idx] for burst_idx in burst_indices]
            scatter_time = [burst_index/self.mcs_reader.sampling_frequency for burst_index in burst_indices]
            if len(plot_time) == len(plot_signal):
                self.plot_widget.plot(plot_time, plot_signal)
            elif len(plot_time) >= len(plot_signal):
                self.plot_widget.plot(plot_time[:-1], plot_signal)
            elif len(plot_time) <= len(plot_signal):
                self.plot_widget.plot(plot_time, plot_signal[:-1])
            self.scatter_plot = pg.ScatterPlotItem(x=scatter_time, y=scatter_amps, size=10, pen=pg.mkPen('r'))
            self.plot_widget.addItem(self.scatter_plot)
        else:
            text = 'no bursts found in channel ' + str(label)
            mssg = pg.TextItem(text)
            self.plot_widget.addItem(mssg)

    def on_burst_detection_thread_finished(self):
        self.progress_label.setText('Finished. :)')
        if self.burst_detection_thread.all_bursts:
            self.all_bursts = self.burst_detection_thread.all_bursts.copy()
        self.burst_detection_thread = None
