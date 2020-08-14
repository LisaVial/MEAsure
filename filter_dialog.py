from PyQt5 import QtCore, QtWidgets
import h5py
import os
from IPython import embed
import pyqtgraph as pg
import numpy as np

from filter_thread import FilterThread


class FilterDialog(QtWidgets.QDialog):
    def __init__(self, parent,  reader):
        super().__init__(parent)
        self.reader = reader
        self.filtered_mat = None
        # embed()

        title = 'Filtering'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)

        self.filtering_thread = None

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.setWindowTitle(title)

        filter_settings_layout = QtWidgets.QVBoxLayout(self)
        filter_settings_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        self.filter_combo_box = QtWidgets.QComboBox(self)
        self.filter_combo_box.setFixedSize(self.width, 25)

        self.filter_combo_box.addItem('Lowpass Filter')
        self.filter_combo_box.addItem('Highpass Filter')
        self.filter_combo_box.addItem('Bandpass Filter')

        self.filter_combo_box.setEditable(True)
        self.filter_combo_box.lineEdit().setReadOnly(True)

        self.filter_combo_box.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.filter_combo_box.currentIndexChanged.connect(self.filter_type_changed)
        filter_settings_layout.addWidget(self.filter_combo_box)

        self.single_cutoff_textbox = QtWidgets.QLineEdit(self)
        self.single_cutoff_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.single_cutoff_textbox.setFixedSize(self.width, 25)
        self.textbox_label = QtWidgets.QLabel('Cutoff frequency [Hz]')
        filter_settings_layout.addWidget(self.single_cutoff_textbox)
        filter_settings_layout.addWidget(self.textbox_label)

        self.second_cutoff_textbox = QtWidgets.QLineEdit(self)
        self.second_cutoff_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.second_cutoff_textbox.setFixedSize(self.width, 25)
        self.second_textbox_label = QtWidgets.QLabel('Upper cutoff frequency [Hz]')
        filter_settings_layout.addWidget(self.second_cutoff_textbox)
        filter_settings_layout.addWidget(self.second_textbox_label)
        self.second_cutoff_textbox.setVisible(False)
        self.second_textbox_label.setVisible(False)

        self.save_filtered_box = QtWidgets.QCheckBox('Save filtered traces')
        self.label_save_filtered_box = QtWidgets.QLabel('Don\'t save filtered traces')
        filter_settings_layout.addWidget(self.save_filtered_box)
        filter_settings_layout.addWidget(self.label_save_filtered_box)
        self.save_filtered_box.stateChanged.connect(self.save_filtered_box_clicked)

        self.filter_start_button = QtWidgets.QPushButton(self)
        self.filter_start_button.setFixedSize(self.width, 25)
        self.filter_start_button.setText('Start filtering')
        self.filter_start_button.clicked.connect(self.initialize_filtering)
        filter_settings_layout.addWidget(self.filter_start_button)

        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far')
        filter_settings_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        filter_settings_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        filter_settings_layout.addWidget(self.progress_bar)

        main_layout.addLayout(filter_settings_layout)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font-size': '10px'}
        self.plot_widget.setLabel('left', 'channel', **styles)
        self.plot_widget.setLabel('bottom', 'time [s]', **styles)
        main_layout.addWidget(self.plot_widget)

        self.signal = [[0, 0, 0, 0]]
        self.filter = [[0, 0, 0, 0]]
        self.time_s = [[0, 0, 0, 0]]
        self.time_f = [[0, 0, 0, 0]]

        pen_1 = pg.mkPen(color='#006e7d')
        self.fs = self.reader.sampling_frequency

        self.unfiltered = self.plot_widget.plot(self.time_s[-1], self.signal[-1], pen=pen_1, name='unfiltered')

        pen_2 = pg.mkPen(color='#a7c9ba')
        self.filtered = self.plot_widget.plot(self.time_f[-1], self.filter[-1], pen=pen_2, name='filtered')
        self.plot_widget.addLegend()

    def initialize_filtering(self):
        filter_mode = self.filter_combo_box.currentIndex()
        cutoff_1 = float(self.single_cutoff_textbox.text())
        cutoff_2 = None
        if self.filter_combo_box.currentIndex() == 2:
            cutoff_2 = float(self.second_cutoff_textbox.text())
        if self.filtered_mat is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('Filtering')
            self.filter_start_button.setEnabled(False)
            self.filtering_thread = FilterThread(self, self.reader, filter_mode, cutoff_1, cutoff_2)
            self.filtering_thread.progress_made.connect(self.on_progress_made)
            self.filtering_thread.operation_changed.connect(self.on_operation_changed)
            self.filtering_thread.data_updated.connect(self.on_data_updated)
            self.filtering_thread.finished.connect(self.on_filter_thread_finished)

            debug_mode = False  # set to 'True' in order to debug with embed
            if debug_mode:
                # synchronous plotting (runs in main thread and thus allows debugging)
                self.filtering_thread.run()
            else:
                # asynchronous plotting (default):
                self.filtering_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately

    def filter_type_changed(self, index):
        self.filter_combo_box.setCurrentIndex(index)
        if index == 2:
            self.textbox_label.setText('Lower cutoff frequency [Hz]')
            self.second_cutoff_textbox.setVisible(True)
            self.second_textbox_label.setVisible(True)

    def save_filtered_box_clicked(self):
        self.label_save_filtered_box.setText('Saving filtered traces to .h5 file at end of filtering')

    def save_filter_mat(self, filter_mat, reader, filename):
        self.label_save_filtered_box.setText('Saving analysis h5 file...')
        if reader.voltage_traces and reader.sampling_frequency and reader.channel_indices and reader.labels and \
                reader.indices:
            with h5py.File(filename, 'w') as hf:
                dset_1 = hf.create_dataset('indices', data=reader.indices, dtype='int')
                dset_2 = hf.create_dataset('raw traces', data=reader.voltage_traces, dtype='f')
                dt = h5py.special_dtype(vlen=str)
                labels = np.array(reader.labels, dtype=dt)
                dset_3 = hf.create_dataset('channel labels', data=labels, dtype=dt)
                dset_4 = hf.create_dataset('channel ids', data=reader.channel_indices, dtype='int')
                dset_5 = hf.create_dataset('sampling frequency', data=reader.sampling_frequency, dtype='f')
                dset_6 = hf.create_dataset('filter', data=filter_mat, dtype='f')
        self.label_save_filtered_box.setText('Filtered traces saved in: ' + filename)

    def open_filter_file(self, filepath):
        hf = h5py.File(filepath, 'r')
        key = list(hf.keys())[0]
        filer_mat = hf[key]
        return filer_mat

    def check_for_filtered_traces(self):
        # scan path of current file, if the desired .h5 file exists
        filtered = self.mea_file[:-3] + '_filtered_test.h5'
        print(filtered)
        if os.path.exists(filtered):
            # if this file already exists, set it as filter_mat
            filter_mat = self.open_filter_file(filtered)
            # show user an answer that informs him/her about the file and asks, if the user wants to filter channels
            # again anyways
            answer = QtWidgets.QMessageBox.information(self, 'Filtered channels already found',
                                                       'Filter channels again?',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.No)
            # depending on the answer of the user, set the found file as filter_mat or set filter_mat to none
            if answer == QtWidgets.QMessageBox.Yes:
                return None
            else:
                return filter_mat
        # in case there is no filter file found, the filter_mat stays none
        else:
            return None

    @QtCore.pyqtSlot(list)
    def on_data_updated(self, data):
        signal, filterd, label = data[0], data[1], data[2]
        ay = self.plot_widget.getAxis('left')
        ticks = [0]
        ay.setTicks([[(v, label) for v in ticks]])

        self.signal.append(signal)

        self.time_s.append(list(np.arange(0, len(self.signal[-1])*(312/self.fs), (312/self.fs))))
        print(len(self.signal[-1]), (312/self.fs))
        # embed()
        self.unfiltered.setData(self.time_s[-1], self.signal[-1])

        self.filter.append(filterd)

        self.time_f.append(list(np.arange(0, len(self.filter[-1])*(312/self.fs), (312/self.fs))))
        self.filtered.setData(self.time_f[-1], self.filter[-1])


    # this function changes the label of the progress bar to inform the user what happens in the background
    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    # this function updates the progress bar
    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")

    def on_filter_thread_finished(self):
        self.progress_label.setText('Finished :)')
        if self.filtering_thread.filtered_mat:
            print('copying new filter mat...')
            self.filtered_mat = self.filtering_thread.filtered_mat.copy()
        self.filtering_thread = None
        self.filter_start_button.setEnabled(True)
        if self.save_filtered_box.isChecked():
            mea_file = self.reader.file.filename
            self.save_filter_mat(self.filtered_mat, self.reader, mea_file[:-3] + '_analysis.h5')
