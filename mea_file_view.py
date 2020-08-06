from PyQt5 import QtWidgets, QtCore
import os
import csv

from plot_widget import PlotWidget
from mea_data_reader import MeaDataReader
from mea_grid import MeaGrid

from spike_detection_dialog import SpikeDetectionDialog
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

        self.spike_detection_window_button = QtWidgets.QPushButton(self)
        self.spike_detection_window_button.setText("Open spike detection")
        self.spike_detection_window_button.clicked.connect(self.open_sd_window)

        grid_buttons_and_progress_bar_layout = QtWidgets.QVBoxLayout(self)
        grid_buttons_and_progress_bar_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        grid_buttons_and_progress_bar_layout.addWidget(self.mea_grid)

        grid_buttons_and_progress_bar_layout.addWidget(self.spike_detection_window_button)

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
        # self.plot_widget.setBackground('w')

        self.figure = self.plot_widget.figure

        main_layout.addWidget(self.plot_widget)

    # def save_spikemat(self, spikemat, filepath):
    #     with open(filepath, 'w') as f:
    #         writer = csv.writer(f)
    #         writer.writerows(spikemat)
    #


    @QtCore.pyqtSlot()
    def open_sd_window(self):
        # self.spike_mat = self.check_for_spike_times_csv(self.mea_file)
        spike_detection_window = SpikeDetectionDialog(None, self.mea_file)
        spike_detection_window.exec_()
        # if self.spike_mat is None:
        #     self.progress_bar.setValue(0)
        #     self.progress_label.setText("")
        #     self.spike_detection_button.setEnabled(False)
        #     self.spike_detection_thread = SpikeDetectionThread(self, self.plot_widget, self.mea_file)
        #     self.spike_detection_thread.finished.connect(self.on_spike_detection_thread_finished)
        #     self.spike_detection_thread.progress_made.connect(self.on_progress_made)
        #     self.spike_detection_thread.operation_changed.connect(self.on_operation_changed)
        #
        #     debug_mode = False  # set to 'True' in order to debug plot creation with embed
        #     if debug_mode:
        #         # synchronous plotting (runs in main thread and thus allows debugging)
        #         self.spike_detection_thread.run()
        #     else:
        #         # asynchronous plotting (default):
        #         self.spike_detection_thread.start()  # start will start thread (and run),
        #         # but main thread will continue immediately


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

    # def save_check_box_clicked(self):
    #     self.label_save_check_box.setText('Saving spikes to .csv file at the end of spike detection')

    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")
    #
    # @QtCore.pyqtSlot()
    # def on_spike_detection_thread_finished(self):
    #     self.progress_label.setText("Finished :)")
    #     if self.spike_detection_thread.spike_mat:
    #         self.spike_mat = self.spike_detection_thread.spike_mat.copy()
    #     self.spike_detection_thread = None
    #     self.spike_detection_button.setEnabled(True)
    #     if self.save_check_box.isChecked():
    #         self.save_spike_mat(self.spike_mat, self.mea_file + '_spiketimes.csv')
    #
    # def save_spike_mat(self, spike_mat, mea_file):
    #     self.label_save_check_box.setText('saving spike times...')
    #     # take filepath and filename, to get name of mea file and save it to the same directory
    #     file_name = mea_file[:-3]
    #     spike_filename = file_name + '_spiketimes.csv'
    #     self.save_spikemat(spike_mat, spike_filename)
        self.label_save_check_box.setText('spike times saved in: ' + spike_filename)

    @QtCore.pyqtSlot()
    def on_plot_creation_thread_finished(self):
        self.progress_label.setText("Finished :)")
        self.plot_creation_thread = None
        self.plot_widget.toolbar.show()
        # self.plot_manager.add_plot(self)
        self.raster_plot_button.setEnabled(True)
        self.plot_widget.refresh_canvas()

