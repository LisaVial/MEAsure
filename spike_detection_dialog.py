from PyQt5 import QtCore, QtWidgets
import os
import pyqtgraph as pg
import numpy as np
import h5py

from spike_detection_thread import SpikeDetectionThread


class SpikeDetectionDialog(QtWidgets.QDialog):
    def __init__(self, parent, reader):
        super().__init__(parent)

        # set variables that come from MEA file reader as class variables
        self.reader = reader

        self.spike_mat = None
        self.spike_indices = None
        self.analysis_file_path = None

        # basic layout of the new spike_detection_dialog
        title = 'Spike detection'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)

        # main layout is the layout for this specific dialog, sub layouts can also be defined and later on be added to
        # the main layout (e.g. if single buttons/plots/whatever should have a defined layout)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.setWindowTitle(title)

        # set spike_detection_thread to none
        self.spike_detection_thread = None

        # implementation of widgets in the spike_detection_dialog
        # save check box is connected to a function that saves spike_mat as .csv file
        self.save_check_box = QtWidgets.QCheckBox("Save spiketimes")
        self.label_save_check_box = QtWidgets.QLabel("Don\'t save spiketimes")
        main_layout.addWidget(self.save_check_box)
        main_layout.addWidget(self.label_save_check_box)
        self.save_check_box.stateChanged.connect(self.save_check_box_clicked)

        # spike_detection_start_button is connected to a function that initializes spike detection thread
        self.spike_detection_start_button = QtWidgets.QPushButton(self)
        self.spike_detection_start_button.setText("Start spike detection")
        self.spike_detection_start_button.clicked.connect(self.initialize_spike_detection)
        main_layout.addWidget(self.spike_detection_start_button)

        # operation and progress_label is linked to the progress bar, so that the user sees, what is happening in the
        # background of the GUI
        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far')
        main_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        main_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setFixedSize(self.width, 25)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font-size': '10px'}
        self.plot_widget.setLabel('left', 'amplitude [&#956;]', **styles)
        self.plot_widget.setLabel('bottom', 'time [s]', **styles)
        main_layout.addWidget(self.plot_widget)

        self.voltage_trace = [[0, 0, 0, 0]]
        self.time_vt = [[0, 0, 0, 0]]
        self.spiketimes = [[0, 0, 0, 0]]
        self.height_spiketimes = [[0, 0, 0, 0]]
        self.threshold = 0

        pen_1 = pg.mkPen(color='#006e7d')
        self.fs = 10000     # ToDo: make sure this is stored as well with .meae file creation

        self.signal_plot = self.plot_widget.plot(self.time_vt[-1], self.voltage_trace[-1], pen=pen_1,
                                                 name='voltage trace')
        pen_thresh = pg.mkPen(color='k')
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pen_thresh)
        self.hLine.setValue(self.threshold)
        self.plot_widget.addItem(self.hLine)
        self.hLine2 = pg.InfiniteLine(angle=0, movable=False, pen=pen_thresh)
        self.hLine2.setValue(-1 * self.threshold)
        self.plot_widget.addItem(self.hLine2)

        pen_2 = pg.mkPen(color='#a7c9ba')
        self.scatter = pg.ScatterPlotItem(pen=pen_2, symbol='|', name='spiketimes')
        self.plot_widget.addItem(self.scatter)
        self.plot_widget.addLegend()

    @QtCore.pyqtSlot()
    def initialize_spike_detection(self):
        if self.spike_mat is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText("")
            self.spike_detection_start_button.setEnabled(False)
            self.spike_detection_thread = SpikeDetectionThread(self, self.reader)
            self.spike_detection_thread.progress_made.connect(self.on_progress_made)
            self.spike_detection_thread.operation_changed.connect(self.on_operation_changed)
            self.spike_detection_thread.data_updated.connect(self.on_data_updated)
            self.spike_detection_thread.finished.connect(self.on_spike_detection_thread_finished)

            debug_mode = False  # set to 'True' in order to debug plot creation with embed
            if debug_mode:
                # synchronous plotting (runs in main thread and thus allows debugging)
                self.spike_detection_thread.run()
            else:
                # asynchronous plotting (default):
                self.spike_detection_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately

    def save_check_box_clicked(self):
        # change label of the save check box in case the user clicked it
        self.label_save_check_box.setText('Saving spikes to .meae file at the end of spike detection')

    # this function changes the label of the progress bar to inform the user what happens in the backgound
    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    # this function updates the progress bar
    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")

    # once the spike_detection_thread is finnished it is set back to None and depending on the save_check_box, the
    # spike_mat is saved to a .csv file
    @QtCore.pyqtSlot()
    def on_spike_detection_thread_finished(self):
        self.progress_label.setText("Finished :)")
        if self.spike_detection_thread.spike_mat:
            self.spike_indices = self.spike_detection_thread.spike_indices.copy()
            self.spike_mat = self.spike_detection_thread.spike_mat.copy()
        self.spike_detection_thread = None
        self.spike_detection_button.setEnabled(True)
        if self.save_check_box.isChecked():
            self.save_spike_mat(self.spike_mat, self.spike_indices, self.mea_file[:-3] + '.meae')

    @QtCore.pyqtSlot(list)
    def on_data_updated(self, data):
        signal, spike_times, threshold = data[0], data[1], data[2]
        spike_times = spike_times * (312/self.fs)
        self.voltage_trace.append(signal)
        self.time_vt.append(list(np.arange(0, len(self.voltage_trace[-1])*(312/self.fs), (312/self.fs))))
        self.signal_plot.setData(self.time_vt[-1], self.voltage_trace[-1])

        self.hLine.setYValue(threshold)
        self.hLine2.setYValue(-1 * threshold)

        self.spiketimes.append(spike_times)
        self.height_spiketimes.append(np.ones(len(spike_times)) * np.max(signal))
        self.scatter.setData(self.spiketimes[-1], self.height_spiketimes[-1])


    # function to save the found spiketimes stored in spike_mat as .csv file
    def save_spike_mat(self, spike_mat, spike_indices, mea_file):
        self.label_save_check_box.setText('saving spike times...')
        # take filepath and filename, to get name of mea file and save it to the same directory
        file_name = mea_file[:-3]
        spike_filename = file_name + 'meae'
        split_path = mea_file.split('\\')
        overall_path = split_path[0] + '\\' + split_path[1] + '\\' + split_path[2]
        analysis_filename = [file for file in os.listdir(overall_path) if file.endswith('.meae')]
        if len(analysis_filename) > 0:
            self.analysis_file_path = overall_path + '\\' + analysis_filename[0]
        if self.analysis_file_path:
            with h5py.File(self.analysis_file_path, 'a') as hf:
                dset_1 = hf.create_dataset('spiketimes', data=spike_mat, dtype='f')
                dset_2 = hf.create_dataset('spiketimes_indices', data=spike_indices, dtype='int')
        else:
            with h5py.File(self.reader.file_path[:-3] + '.meae', 'w') as hf:
                dset_1 = hf.create_dataset('spiketimes', data=spike_mat, dtype='f')
                dset_2 = hf.create_dataset('spiketimes_indices', data=spike_indices, dtype='int')
        self.label_save_check_box.setText('spike times saved in: ' + spike_filename)

    # function to open spike_mat .csv in case it exists
    # def open_spikemat(self, filepath):
    #     with open(filepath, 'r') as read_obj:
    #         csv_reader = csv.reader(read_obj)
    #         spike_mat = list(csv_reader)
    #     return spike_mat

