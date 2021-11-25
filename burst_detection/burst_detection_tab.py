from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg

from burst_detection.burst_detection_thread import BurstDetectionThread


class BurstDetectionTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_indices, grid_labels, settings):
        super().__init__(parent)
        self.reader = reader
        self.grid_indices = grid_indices
        self.grid_labels = grid_labels
        self.settings = settings

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        operation_layout = QtWidgets.Qt.QVBoxLayout(self)
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

        self.burst_detection_thread = None

    def initialize_burst_detection(self):
        if self.burst_detection_thread is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText('Detecting bursts')
            self.burst_detection_thread = BurstDetectionThread(self)
            self.burst_detection_thread.progress_made.connect(self.on_progress_made)
            self.burst_detection_thread.operation_changed.connect(self.on_operation_changed)
            self.burst_detection_thread.data_updated.connect(self.on_data_updated)
            self.burst_detection_thread.finished.connect(self.on_burst_detection_thread_finished)

    def on_progress_made(self):
        pass

    def on_operation_changed(self):
        pass

    def on_data_updated(self):
        pass

    def on_burst_detection_thread_finished(self):
        pass