from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np

from burst_detection.burst_detection_thread import BurstDetectionThread


class BurstDetectionTab(QtWidgets.QWidget):
    def __init__(self, parent, mcs_reader, sc_reader, grid_indices, grid_labels, settings):
        super().__init__(parent)
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
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

        self.raw_trace_plot = None
        self.scatter_plot = None

        self.burst_detection_thread = None
        self.all_bursts = None

    def initialize_burst_detection(self):
        if self.burst_detection_thread is None:
            self.progress_bar.setValue(0)
            self.operation_label.setText('Initializing burst detection.')
            self.burst_detection_thread = BurstDetectionThread(self, self.sc_reader.spiketimes, self.grid_labels,
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
        label = data[0]
        burst_indices = data[1]
        raw_signal = self.mcs_reader.get_scaled_channel(label)
        raw_time = np.arange(0, len(raw_signal), 1/self.mcs_reader.sampling_frequency)
        scatter_amps = [raw_signal[burst_idx] for burst_idx in burst_indices]
        scatter_time = [burst_index * self.mcs_reader.sampling_frequency for burst_index in burst_indices]
        self.raw_trace_plot = pg.plot(raw_time, raw_signal)
        self.scatter_plot = pg.ScatterPlotItem(size=10, brush=pg.mkBrush('grey'))
        spots = [{'pos': scatter_time[i], 'data': scatter_amps[i]} for i in range(len(scatter_time))]
        self.scatter_plot.addPoints(spots)
        self.plot_widget.addItem(self.raw_trace_plot)
        self.plot_widget.addItem(self.scatter_plot)

    def on_burst_detection_thread_finished(self):
        self.progress_label.setText('Finished. :)')
        if self.burst_detection_thread.all_bursts:
            self.all_bursts = self.burst_detection_thread.all_bursts.copy()
        self.burst_detection_thread = None
