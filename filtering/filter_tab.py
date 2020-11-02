from PyQt5 import QtCore, QtWidgets
import h5py
import os
import pyqtgraph as pg
import numpy as np

from settings import Settings
from filtering.filter_thread import FilterThread
from filtering.filter_settings_dialog import FilterSettingsDialog


class FilterTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings

        self.filtered_mat = None

        self.filtering_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        # ToDo: change this to mea_file_view or delete progress bar in mea file view
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
        self.progress_bar.setTextVisible(True)
        operation_layout.addWidget(self.progress_bar)

        main_layout.addLayout(operation_layout)

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
        filter_mode = self.settings.mode
        cutoff_1 = float(self.settings.lower_cutoff)
        cutoff_2 = None
        if self.settings.mode == 2:
            cutoff_2 = float(self.settings.upper_cutoff)
        if self.filtered_mat is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('Filtering')
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

    def save_filter_mat(self, filter_mat, filename, reader):
        self.operation_label.setText('Saving filtered traces im .meae file...')
        if reader.voltage_traces and reader.sampling_frequency and reader.channel_indices and reader.labels:
            with h5py.File(filename, 'w') as hf:
                dset_1 = hf.create_dataset('filter', data=filter_mat)
                dset_2 = hf.create_dataset('fs', data=reader.sampling_frequency)
                dset_3 = hf.create_dataset('channel_indices', data=reader.channel_indices)
                save_labels = [label.encode('utf-8') for label in reader.labels]
                dset_3 = hf.create_dataset('channel_labels', data=save_labels)
        self.operation_label.setText('Filtered traces saved in: ' + filename)

    def open_filter_file(self, filepath):
        hf = h5py.File(filepath, 'r')
        key = list(hf.keys())[0]
        filer_mat = hf[key]
        return filer_mat

    def check_for_filtered_traces(self):
        # scan path of current file, if the desired .h5 file exists
        filtered = self.mea_file[:-3] + '_filtered.h5'
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

        if self.settings.save_filtered_traces:
            self.save_filter_mat(self.filtered_mat, self.reader.file_path[:-3] + '.meae', self.reader)