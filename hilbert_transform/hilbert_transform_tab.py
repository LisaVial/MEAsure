from PyQt5 import QtCore, QtWidgets
import numpy as np

from hilbert_transform.hilbert_transform_thread import HilbertTransformThread
from results import ResultStoring

import pyqtgraph as pg
from plot_manager import PlotManager


class HilbertTransformTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_labels, settings):
        super().__init__(parent)
        self.mea_file_view = parent

        self.reader = reader
        self.grid_labels = grid_labels
        self.settings = settings
        self.threshold_factor = self.settings.threshold_factor
        self.min_peaks_per_seizure = self.settings.min_peaks_per_seizure

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        operation_layout = QtWidgets.QVBoxLayout(self)
        operation_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far')
        operation_layout.addWidget(self.operation_label)

        self.progress_label = QtWidgets.QLabel(self)
        operation_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setVisible(True)
        operation_layout.addWidget(self.progress_bar)
        main_layout.addLayout(operation_layout)

        tool_button_layout = QtWidgets.QVBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save results...")
        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.save_button.setEnabled(False)  # will be enabled after plotting
        tool_button_layout.addWidget(self.save_button)

        main_layout.addLayout(tool_button_layout)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font size': '10 px'}
        self.plot_widget.setLabel('left', 'amplitude', units='<font>&mu;V</font>', **styles)
        self.plot_widget.setLabel('bottom', 'time', units='<font>s</font>', **styles)
        main_layout.addWidget(self.plot_widget)

        self.binned_time = np.linspace(0, int(np.ceil(self.reader.duration)), int(np.ceil(self.reader.duration)))
        self.binned_values = np.zeros(len(self.binned_time))
        self.threshold = 1
        self.dashed_line_pen = pg.mkPen(width=1.5, style=QtCore.Qt.DashLine)
        self.line = pg.InfiniteLine(pos=self.threshold, angle=0, pen=self.dashed_line_pen, movable=False)
        self.bar_graph = pg.BarGraphItem(x=self.binned_time, height=self.binned_values, width=1, pen=pg.mkPen('b',
                                                                                                              width=1))
        self.red_bars_graph = pg.BarGraphItem(x=[0, 1], height=[0, 0], width=1, pen=pg.mkPen('r', width=1))

        self.plot_widget.addItem(self.bar_graph)
        self.plot_widget.addItem(self.red_bars_graph)
        self.plot_widget.addItem(self.line)

        self.hilbert_transform_thread = None

        self.epileptic_indices = []

        self.initialize_hilbert_transform()

    def initialize_hilbert_transform(self):
        if self.hilbert_transform_thread is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('Calculating Hilbert Transform')
            # To Do: check inputs to the thread class
            self.hilbert_transform_thread = HilbertTransformThread(self, self.reader, self.grid_labels,
                                                                   self.threshold_factor, self.min_peaks_per_seizure)
            self.hilbert_transform_thread.progress_made.connect(self.on_progress_made)
            self.hilbert_transform_thread.operation_changed.connect(self.on_operation_changed)
            self.hilbert_transform_thread.data_updated.connect(self.on_data_updated)
            self.hilbert_transform_thread.finished.connect(self.on_hilbert_transform_thread_finished)

            debug_mode = False
            if debug_mode:
                self.hilbert_transform_thread.run()
            else:
                self.hilbert_transform_thread.start()

    @QtCore.pyqtSlot(list)
    def on_data_updated(self, data):
        self.binned_time = np.array(data[0])
        self.binned_values = np.array(data[1])
        self.threshold = data[2]
        self.epileptic_indices.append(data[3])
        epileptic_indices_channel = data[3]

        unepileptic_times = [self.binned_time[idx] for idx in range(len(self.binned_time))
                             if idx not in epileptic_indices_channel]
        unepileptic_values = [self.binned_values[idx] for idx in range(len(self.binned_values))
                              if idx not in epileptic_indices_channel]

        self.line = pg.InfiniteLine(pos=self.threshold, angle=0, pen=self.dashed_line_pen, movable=False)
        self.plot_widget.clear()
        self.bar_graph = pg.BarGraphItem(x=unepileptic_times[:-1], height=unepileptic_values, width=1,
                                         pen=pg.mkPen('b', width=1))
        self.red_bars_graph = pg.BarGraphItem(x=self.binned_time[epileptic_indices_channel],
                                              height=self.binned_values[epileptic_indices_channel], width=1,
                                              pen=pg.mkPen('r', width=1))
        self.plot_widget.addItem(self.bar_graph)
        self.plot_widget.addItem(self.red_bars_graph)
        self.plot_widget.addItem(self.line)

    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + '%')

    @QtCore.pyqtSlot()
    def on_hilbert_transform_thread_finished(self):
        self.progress_label.setText('Finished. :)')

        if self.hilbert_transform_thread.epileptic_indices:
            self.epileptic_indices = self.hilbert_transform_thread.epileptic_indices.copy()
            self.mea_file_view.results.set_hilbert_transform_data(self.epileptic_indices)

        self.hilbert_transform_thread = None
        self.save_button.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_save_button_clicked(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setNameFilter("CSV files (*.csv)")
        file_dialog.setDefaultSuffix(".csv")
        file_dialog_result = file_dialog.exec()
        if file_dialog_result:
            # user selected file:
            selected_file = file_dialog.selectedFiles()[0]
            self.mea_file_view.results.save_hilbert_transform_data_to(selected_file)

