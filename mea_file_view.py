from PyQt5 import QtWidgets, QtCore
import os
import csv

from plot_widget import PlotWidget
from mea_data_reader import MeaDataReader
from mea_grid import MeaGrid

from spike_detection_dialog import SpikeDetectionDialog
from filter_dialog import FilterDialog
from plot_creation_thread import PlotCreationThread


class MeaFileView(QtWidgets.QWidget):
    def __init__(self, parent, mea_file):
        super().__init__(parent)
        self.reader = MeaDataReader()
        self.mea_file = mea_file

        self.plot_creation_thread = None

        self.mea_grid = MeaGrid(self)
        self.mea_grid.setFixedSize(600, 600)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        grid_buttons_and_progress_bar_layout = QtWidgets.QVBoxLayout(self)
        grid_buttons_and_progress_bar_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        grid_buttons_and_progress_bar_layout.addWidget(self.mea_grid)

        self.filter_dialog_button = QtWidgets.QPushButton(self)
        self.filter_dialog_button.setText('Open filtering dialog')
        self.filter_dialog_button.clicked.connect(self.open_filter_dialog)
        grid_buttons_and_progress_bar_layout.addWidget(self.filter_dialog_button)

        self.spike_detection_dialog_button = QtWidgets.QPushButton(self)
        self.spike_detection_dialog_button.setText("Open spike detection dialog")
        self.spike_detection_dialog_button.clicked.connect(self.open_sd_dialog)
        grid_buttons_and_progress_bar_layout.addWidget(self.spike_detection_dialog_button)

        self.raster_plot_button = QtWidgets.QPushButton(self)
        self.raster_plot_button.setText("Raster Plot")

        grid_buttons_and_progress_bar_layout.addWidget(self.raster_plot_button)

        self.operation_label = QtWidgets.QLabel(self)
        grid_buttons_and_progress_bar_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        grid_buttons_and_progress_bar_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        grid_buttons_and_progress_bar_layout.addWidget(self.progress_bar)
        main_layout.addLayout(grid_buttons_and_progress_bar_layout)
        self.raster_plot_button.clicked.connect(self.initialize_plotting)

        self.plot_widget = PlotWidget(self)

        self.figure = self.plot_widget.figure

        main_layout.addWidget(self.plot_widget)

    @QtCore.pyqtSlot()
    def open_sd_dialog(self):
        spike_detection_dialog = SpikeDetectionDialog(None, self.mea_file)
        spike_detection_dialog.exec_()

    @QtCore.pyqtSlot()
    def open_filter_dialog(self):
        filter_dialog = FilterDialog(None, self.mea_file)
        filter_dialog.exec_()

    @QtCore.pyqtSlot()
    def initialize_plotting(self):
        if self.spike_mat is None:
            spiketimes_csv = self.mea_file[:-3] + '_spiketimes.csv'
            if os.path.exists(spiketimes_csv):
                self.spike_mat = self.open_spikemat(spiketimes_csv)
            else:
                QtWidgets.QMessageBox.information(self, 'no spiketimes found', 'Please click spike detection button')
        if self.spike_mat is not None:
            self.progress_bar.setValue(0)
            self.progress_label.setText("")
            self.raster_plot_button.setEnabled(False)
            self.plot_creation_thread = PlotCreationThread(self.plot_widget, self.spike_mat)
            self.plot_creation_thread.finished.connect(self.on_plot_creation_thread_finished)
            self.plot_creation_thread.progress_made.connect(self.on_progress_made)
            self.plot_creation_thread.operation_changed.connect(self.on_operation_changed)

            debug_mode = True  # set to 'True' in order to debug plot creation with embed
            if debug_mode:
                # synchronous plotting (runs in main thread and thus allows debugging)
                self.plot_creation_thread.run()
            else:
                # asynchronous plotting (default):
                self.plot_creation_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately

    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")

    @QtCore.pyqtSlot()
    def on_plot_creation_thread_finished(self):
        self.progress_label.setText("Finished :)")
        self.plot_creation_thread = None
        self.plot_widget.toolbar.show()
        # self.plot_manager.add_plot(self)
        self.raster_plot_button.setEnabled(True)
        self.plot_widget.refresh_canvas()

