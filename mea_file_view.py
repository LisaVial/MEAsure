from PyQt5 import QtWidgets, QtCore
import os
import csv
from pyqtgraph import PlotWidget
import pyqtgraph as pg

from mea_data_reader import MeaDataReader
from mea_grid import MeaGrid
from spike_detection_thread import SpikeDetectionThread
from plot_creation_thread import PlotCreationThread
from plot_widget import PlotWidget


class MeaFileView(QtWidgets.QWidget):
    def __init__(self, parent, mea_file):
        super().__init__(parent)
        self.reader = MeaDataReader()
        self.mea_file = mea_file
        self.spike_mat = None

        self.mea_grid = MeaGrid(self)
        self.mea_grid.setFixedSize(600, 600)

        self.spike_detection_thread = None
        self.plot_creation_thread = None

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.spike_detection_button = QtWidgets.QPushButton(self)
        self.spike_detection_button.setText("Spike Detection")

        grid_buttons_and_progress_bar_layout = QtWidgets.QVBoxLayout(self)
        grid_buttons_and_progress_bar_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        grid_buttons_and_progress_bar_layout.addWidget(self.mea_grid)

        self.save_check_box = QtWidgets.QCheckBox("save spike times")
        self.label_save_check_box = QtWidgets.QLabel("don't save spike times")

        self.save_check_box.stateChanged.connect(self.save_check_box_clicked)

        grid_buttons_and_progress_bar_layout.addWidget(self.save_check_box)
        grid_buttons_and_progress_bar_layout.addWidget(self.label_save_check_box)
        grid_buttons_and_progress_bar_layout.addWidget(self.spike_detection_button)

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
        self.spike_detection_button.clicked.connect(self.initialize_spike_detection)
        self.raster_plot_button.clicked.connect(self.initialize_plotting)

        self.plot_widget = PlotWidget(self)
        # self.plot_widget.setBackground('w')

        # self.figure = self.plot_widget.figure
        # self.previous_button = QtWidgets.QPushButton(self)
        # self.previous_button.setText("<")
        # self.previous_button.pressed.connect(self.on_previous_button_pressed)
        #
        # self.next_button = QtWidgets.QPushButton(self)
        # self.next_button.setText(">")
        # self.next_button.pressed.connect(self.on_next_button_pressed)

        buttons_layout = QtWidgets.QHBoxLayout()
        # buttons_layout.addWidget(self.previous_button)
        # buttons_layout.addWidget(self.next_button)
        main_layout.addWidget(self.plot_widget)
        # main_layout.addWidget(self.previous_button)
        # main_layout.addWidget(self.next_button)

    # @QtCore.pyqtSlot()
    # def on_previous_button_pressed(self):
    #     self.index -= 1
    #     self.previous_button.setEnabled(self.index > 0)
    #     self.next_button.setEnabled(self.index < self.max_index - 1)
    #     self.show_plot(self.index)
    #
    # @QtCore.pyqtSlot()
    # def on_next_button_pressed(self):
    #     self.index += 1
    #     self.previous_button.setEnabled(self.index > 0)
    #     self.next_button.setEnabled(self.index < self.max_index - 1)
    #     self.show_plot(self.index)

    def save_spikemat(self, spikemat, filepath):
        with open(filepath, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(spikemat)

    def open_spikemat(self, filepath):
        with open(filepath, 'r') as read_obj:
            csv_reader = csv.reader(read_obj)
            spike_mat = list(csv_reader)
        return spike_mat

    def check_for_spike_times_csv(self, mea_file):
        spiketimes_csv = mea_file[:-3] + '_spiketimes.csv'
        if os.path.exists(spiketimes_csv):
            spike_mat = self.open_spikemat(spiketimes_csv)

            answer = QtWidgets.QMessageBox.information(self, 'spiketimes already found', 'Detect spikes again?',
                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                              QtWidgets.QMessageBox.No)

            if answer == QtWidgets.QMessageBox.Yes:
                return None
            else:
                return spike_mat
        else:
            return None

    @QtCore.pyqtSlot()
    def initialize_spike_detection(self):
        self.spike_mat = self.check_for_spike_times_csv(self.mea_file)
        if self.spike_mat is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText("")
            self.spike_detection_button.setEnabled(False)
            self.spike_detection_thread = SpikeDetectionThread(self, self.plot_widget, self.mea_file)
            self.spike_detection_thread.finished.connect(self.on_spike_detection_thread_finished)
            self.spike_detection_thread.progress_made.connect(self.on_progress_made)
            self.spike_detection_thread.operation_changed.connect(self.on_operation_changed)

            debug_mode = False  # set to 'True' in order to debug plot creation with embed
            if debug_mode:
                # synchronous plotting (runs in main thread and thus allows debugging)
                self.spike_detection_thread.run()
            else:
                # asynchronous plotting (default):
                self.spike_detection_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately


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

    def save_check_box_clicked(self):
        self.label_save_check_box.setText('Saving spikes to .csv file at the end of spike detection')

    def save_filtered_box_clicked(self):
        self.label_save_filtered_box.setText('Saving filtered traces to .h5 file at the end of filtering')

    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")

    @QtCore.pyqtSlot()
    def on_spike_detection_thread_finished(self):
        self.progress_label.setText("Finished :)")
        if self.spike_detection_thread.spike_mat:
            self.spike_mat = self.spike_detection_thread.spike_mat.copy()
        self.spike_detection_thread = None
        self.spike_detection_button.setEnabled(True)
        if self.save_check_box.isChecked():
            self.save_spike_mat(self.spike_mat, self.mea_file + '_spiketimes.csv')

    def save_spike_mat(self, spike_mat, mea_file):
        self.label_save_check_box.setText('saving spike times...')
        # take filepath and filename, to get name of mea file and save it to the same directory
        file_name = mea_file[:-3]
        spike_filename = file_name + '_spiketimes.csv'
        self.save_spikemat(spike_mat, spike_filename)
        self.label_save_check_box.setText('spike times saved in: ' + spike_filename)

    @QtCore.pyqtSlot()
    def on_plot_creation_thread_finished(self):
        self.progress_label.setText("Finished :)")
        self.plot_creation_thread = None
        self.plot_widget.toolbar.show()
        # self.plot_manager.add_plot(self)
        self.raster_plot_button.setEnabled(True)
        self.plot_widget.refresh_canvas()

