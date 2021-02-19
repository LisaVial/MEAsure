from PyQt5 import QtCore, QtWidgets
import h5py
import os
import pyqtgraph as pg
import numpy as np

from results import ResultStoring
from filtering.filter_thread import FilterThread


# Here the tab widget, which will be added to the mea_file_view, is created. This class handles the visualization of
# what is going on in the background by a pyqtgraph plot widget which plots data live. Also, in this class a QThread
# is initialized, which will compute the filtering in the background, while the GUI will remain responsive.

# The QWidget class is used whenever you want to create a quite customized widget.
class FilterTab(QtWidgets.QWidget):
    # The FilterTab class receives the MeaFileView as a parent (where it will be embedded), the McsDataReader (another
    # class, which handles the reading of the h5 files of the recordings), the grid  (either all or a selection of grid
    # channels) and the filter settings.
    def __init__(self, parent, meae_filename, reader, grid_indices, append, settings):
        super().__init__(parent)
        # By setting variables to class variables (done with the 'self.' in front of them) it enables you to use them
        # outside this __init__() function. For example in functions you created yourself further down in the script.
        self.meae_filename = meae_filename
        self.reader = reader
        self.grid_indices = grid_indices
        self.append_existing_file = append
        self.settings = settings
        self.mea_file_view = parent

        # Line 28 and 29 set two class variables to None. This is convenient for the handling of the Thread. As long as
        # the filtering_thread is None, there is no Thread running.
        self.filtered_mat = None
        self.filtering_thread = None

        # Line 33 - 51 sets up different widgets (for detailed explanation see filter_settings_dialog.py and
        # filter_settings_widget.py)
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
        self.progress_bar.setTextVisible(True)
        operation_layout.addWidget(self.progress_bar)

        main_layout.addLayout(operation_layout)

        # Line 54 - 73 sets up the pyqtgraph plot widget. Pyqtgraph is a python library designed to enable its users
        # to plot data fast when using PyQt5. The look of the graphs is not as sophisticated as with matplotlib,
        # but the plotting works much faster. So, for any live plotting in MEAsure, the pyqtgraph library is used,
        # while for plotting only circumstances matplotlib is used
        self.plot_widget = pg.PlotWidget()
        # pyqtgraph uses the PyQt5 platform to plot, the setting up of plots works a little different. Happily, their
        # documentation is good (https://pyqtgraph.readthedocs.io/en/latest/index.html) and there are many examples to
        # be found there
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font-size': '10px'}
        self.plot_widget.setLabel('left', 'channel', **styles)
        self.plot_widget.setLabel('bottom', 'time [s]', **styles)
        main_layout.addWidget(self.plot_widget)

        # To be able to show the plot as soon as the tab is added to MeaFileView it needs some variables to plot. So
        # all the needed variables are set to zero at first.
        self.signal = [[0, 0, 0, 0]]
        self.filter = [[0, 0, 0, 0]]
        self.time_s = [[0, 0, 0, 0]]
        self.time_f = [[0, 0, 0, 0]]

        # With the pens in pyqtgraph you design the appearance of your plots
        pen_1 = pg.mkPen(color='#006e7d')
        self.fs = self.reader.sampling_frequency

        # the plot functionality is initially the same as with matplotlib. Later on (in the function on_data_updated in
        # this script), the function setData() will be used.
        self.unfiltered = self.plot_widget.plot(self.time_s[-1], self.signal[-1], pen=pen_1, name='unfiltered')

        pen_2 = pg.mkPen(color='#a7c9ba')
        self.filtered = self.plot_widget.plot(self.time_f[-1], self.filter[-1], pen=pen_2, name='filtered')
        self.plot_widget.addLegend()

    def initialize_filtering(self):
        """
        This function sets up the QThread for filtering
        :return: filtered_mat on triggering other functions, once the QThread is finnished.
        """
        # First we get the settings.
        filter_mode = self.settings.mode
        cutoff_1 = float(self.settings.lower_cutoff)
        cutoff_2 = None
        if self.settings.mode == 2:
            cutoff_2 = float(self.settings.upper_cutoff)
        # if self.settings.channel_selection == 1:

        # Here, it is checked if filtered_mat is None or if it already exists. If it exists, the thread has run before
        # or currently runs.
        if self.filtered_mat is None:
            # Line 103 - 105 are only GUI changes, to tell the user what is going on.
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('Filtering')
            # Here, the thread is initialized. We pass the McsDataReader and the setting variables to the Thread.
            self.filtering_thread = FilterThread(self, self.reader, filter_mode, cutoff_1, cutoff_2, self.grid_indices)
            # The thread sends different signals to this FilterTab. So we have to connect the signals to defined
            # functions.
            self.filtering_thread.progress_made.connect(self.on_progress_made)
            self.filtering_thread.operation_changed.connect(self.on_operation_changed)
            self.filtering_thread.data_updated.connect(self.on_data_updated)
            self.filtering_thread.finished.connect(self.on_filter_thread_finished)

            # Line 116 - 122 are needed to actually start the thread, so in this case, the filtering of the traces.
            debug_mode = False  # set to 'True' in order to debug with embed
            if debug_mode:
                # synchronous filtering (runs in main thread and thus allows debugging)
                self.filtering_thread.run()
            else:
                # asynchronous filtering (default):
                self.filtering_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately

    @QtCore.pyqtSlot(list)
    def on_data_updated(self, data):
        """
        This function handles the on_data_updated signal of the filtering thread. With this signal an update of the
        plot_widget (live plot) is triggered.
        :param data: list of unfiltered and filtered signal and the channel label.
        :return: updated plot widget with the unfiltered and filtered signal of the lastly filtered channel
        """
        signal, filterd, label = data[0], data[1], data[2]  # unpacking of the list got as signal
        # Line 135 - 137 sets the current channel label es ytick
        ay = self.plot_widget.getAxis('left')
        ticks = [0]
        ay.setTicks([[(v, label) for v in ticks]])

        # First, the current channel unfiltered signal has to be appended to the list
        self.signal.append(signal)
        # Normally, it would be enough to define this time list once, but I have not yet found out how to do so.
        self.time_s.append(list(np.arange(0, len(self.signal[-1])*(312/self.fs), (312/self.fs))))
        # unfiltered is the plot_widget with the first pen which was set and by
        # setData(self.time_s[-1], self.signal[-1]) the last entries of the individual lists are plotted
        self.unfiltered.setData(self.time_s[-1], self.signal[-1])

        # Same procedure as for unfiltered.
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
        """
        This function is triggered once the QThread is finnished. It shows this information in the GUI, but also
        initializes the saving of filtered traces to a .meae (basically .h5, but i just renamend the file format) file,
        if it is set in the settings to do so.
        :return: saved .meae file if it is set, self.filtering_thread is set to None again
        """
        self.progress_label.setText('Finished :)')
        if self.filtering_thread.filtered_mat:
            self.filtered_mat = self.filtering_thread.filtered_mat.copy()
            self.mea_file_view.results.set_filter_mat(self.filtering_thread.filtered_mat)
        self.filtering_thread = None

        if self.settings.save_filtered_traces:
            path = os.path.split(self.reader.file_path)[0]
            if self.meae_filename is None:
                self.meae_filename = os.path.split(self.reader.file_path)[-1][:-3] + '.meae'
            self.save_filter_mat(self.filtered_mat, os.path.join(path, self.meae_filename), self.reader)

    def save_filter_mat(self, filter_mat, filename, reader):
        """
        This function saves the filtered_mat once the filtering thread is finished
        :param filter_mat: list of arrays of filtered traces
        :param filename: filename under which .meae file will be stored
        :param reader: McsReader, currently used to get filename
        :return:
        """
        if self.append_existing_file:
            self.operation_label.setText('Saving filtered traces im .meae file...')
            with h5py.File(filename, 'a') as hf:
                if 'filter' in hf.keys():
                    hf['filter'].resize((hf['filter'].shape[0] + filter_mat.shape[0]), axis=0)
                    hf['filter'][-filter_mat.shape[0]:] = filter_mat
                self.operation_label.setText('Filtered traces saved in: ' + filename)
        else:
            self.operation_label.setText('Saving filtered traces im .meae file...')
            if reader.sampling_frequency and reader.channel_ids and reader.labels:
                with h5py.File(filename, 'w') as hf:
                    dset_1 = hf.create_dataset('filter', data=filter_mat)
                    dset_2 = hf.create_dataset('fs', data=reader.sampling_frequency)
                    # dset_3 = hf.create_dataset('channel_ids', data=reader.channel_ids)
                    # save_labels = [label.encode('utf-8') for label in reader.labels]
                    # dset_3 = hf.create_dataset('channel_labels', data=save_labels)
            self.operation_label.setText('Filtered traces saved in: ' + filename)


    def open_filter_file(self, filepath):
        """
        This function loads the filtered traces matrix, if it already exists
        :param filepath: filepath of the .meae file
        :return: filter_mat, a .h5 file which holds already filtered traces
        """
        # todo: check if this function is still functional
        hf = h5py.File(filepath, 'r')
        key = list(hf.keys())[0]
        filer_mat = hf[key]
        return filer_mat

    def check_for_filtered_traces(self):
        # scan path of current file, if the desired .meae file exists
        # todo: check if it still works
        filtered = self.mea_file[:-3] + '.meae'
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

    # todo: make tab closeable
    def is_busy_filtering(self):
        return self.filtering_thread is not None

    def can_be_closed(self):
        # only allow closing if not busy
        return not self.is_busy_filtering()
