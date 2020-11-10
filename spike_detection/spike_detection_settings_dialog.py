from PyQt5 import QtCore, QtWidgets, QtGui
import os
import pyqtgraph as pg
import numpy as np
import h5py

from settings import Settings
from spike_detection.spike_detection_thread import SpikeDetectionThread
from settings_dialog import SettingsDialog
from spike_detection.spike_detection_settings import SpikeDetectionSettings


class SpikeDetectionDialog(QtWidgets.QDialog):
    def __init__(self, parent, reader):
        super().__init__(parent)

        # set variables that come from MEA file reader as class variables
        self.reader = reader

        self.settings = Settings.instance.spike_detection_settings

        # basic layout of the new spike_detection_dialog
        title = 'Spike detection'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
        # self.width = 800
        # self.height = 600
        # self.resize(self.width, self.height)

        # main layout is the layout for this specific dialog, sub layouts can also be defined and later on be added to
        # the main layout (e.g. if single buttons/plots/whatever should have a defined layout)
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.setWindowTitle(title)

        # set spike_detection_thread to none
        self.spike_detection_thread = None

        self.spike_mat = None
        self.spike_indices = None
        self.analysis_file_path = None

        spike_detection_settings_layout = QtWidgets.QVBoxLayout(self)
        spike_detection_settings_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        self.settings_button = QtWidgets.QPushButton(self)
        self.settings_button.setText("Settings")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        spike_detection_settings_layout.addWidget(self.settings_button)

        # implementation of widgets in the spike_detection_dialog
        # save check box is connected to a function that saves spike_mat as .csv file
        self.save_check_box = QtWidgets.QCheckBox("Save spiketimes")
        self.label_save_check_box = QtWidgets.QLabel("Don\'t save spiketimes")
        spike_detection_settings_layout.addWidget(self.save_check_box)
        spike_detection_settings_layout.addWidget(self.label_save_check_box)
        self.save_check_box.stateChanged.connect(self.save_check_box_clicked)

        # spike_detection_start_button is connected to a function that initializes spike detection thread
        self.spike_detection_start_button = QtWidgets.QPushButton(self)
        self.spike_detection_start_button.setText("Start spike detection")
        self.spike_detection_start_button.clicked.connect(self.initialize_spike_detection)
        spike_detection_settings_layout.addWidget(self.spike_detection_start_button)

        # operation and progress_label is linked to the progress bar, so that the user sees, what is happening in the
        # background of the GUI
        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far')
        spike_detection_settings_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        spike_detection_settings_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        # self.progress_bar.setFixedSize(self.width, 25)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        spike_detection_settings_layout.addWidget(self.progress_bar)

        # set styles for plot
        styles = {'color': 'k', 'font-size': '10px'}
        # get sampling frequency, this is important for time ratios in plots
        self.fs = self.reader.sampling_frequency

        # open plot that will show raster plot of overall spiketimes of a channel, this will be portrayed at the bottom
        # on the left handside, that is why it is added to the spike_detection_settings_layout
        self.channel_raster_plot = pg.GraphicsLayoutWidget()
        self.channel_raster_plot.useOpenGL(True)
        self.channel_raster_plot.setBackground('w')

        self.timer = pg.QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timer)

        vtick = QtGui.QPainterPath()
        vtick.moveTo(0, -0.5)
        vtick.lineTo(0, 0.5)

        p1 = self.channel_raster_plot.addPlot(row=0, col=0)
        p1.setXRange(-0.05, 1.05)
        p1.hideAxis('bottom')

        s1 = pg.ScatterPlotItem(pxMode=False)
        s1.setSymbol(vtick)
        s1.setSize(1)
        s1.setPen(QtGui.QColor('#d0797a'))
        p1.addItem(s1)

        s2 = pg.ScatterPlotItem(pxMode=False, symbol=vtick, size=1,
                                pen=QtGui.QColor('#d0797a'))
        p1.addItem(s2)
        self.spis = [s1, s2]
        spike_detection_settings_layout.addWidget(self.channel_raster_plot)
        main_layout.addLayout(spike_detection_settings_layout)

        # open plot that will portray single spikes that are found, it will be portrayed on the right side of the
        # dialog, this is why it is added to the main layout
        self.single_spike_plot = pg.PlotWidget()
        self.single_spike_plot.setBackground('w')
        self.single_spike_plot.setLabel('left', 'amplitude [&#956;V]', **styles)
        self.single_spike_plot.setLabel('bottom', 'time [s]', **styles)
        main_layout.addWidget(self.single_spike_plot)

        # set up initial values to plot (everything is set to zero with dimensions according to default values of
        # settings
        # self.voltage_trace = [np.zeros(self.settings.spike_window * self.reader.fs)]
        self.voltage_trace = [[0, 0, 0, 0]]
        # self.time_vt = [np.zeros(self.settings.spike_window * self.reader.fs)]
        self.time_vt = [[0, 0, 0, 0]]
        self.spike_indices = [[0]]
        self.spike_height = [[0]]
        self.threshold = 0

        # plot initial values
        pen_spike_voltage = pg.mkPen(color='#006e7d')
        self.signal_plot = self.single_spike_plot.plot(self.time_vt[-1], self.voltage_trace[-1], pen=pen_spike_voltage,
                                                       name='voltage trace')
        pen_thresh = pg.mkPen(color='k')
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pen_thresh)
        self.hLine.setValue(self.threshold)
        self.single_spike_plot.addItem(self.hLine)
        self.hLine2 = pg.InfiniteLine(angle=0, movable=False, pen=pen_thresh)
        self.hLine2.setValue(-1 * self.threshold)
        self.single_spike_plot.addItem(self.hLine2)

        self.scatter = self.single_spike_plot.plot(pen=None, symbol='o', name='spiketimes')
        self.single_spike_plot.addLegend()

    def on_channel_data_updated(self, data):
        spiketimes = data[0]
        self.spis[-1].setData(spiketimes, 0 + 0.5 + np.zeros((len(spiketimes))))

    @QtCore.pyqtSlot()
    def open_settings_dialog(self):
        settings_dialog = SettingsDialog(self, self.settings)
        if settings_dialog.exec() == 1:  # 'ok' clicked
            self.settings = settings_dialog.get_settings()
            # overwrite global settings as well
            Settings.instance.spike_detection_settings = self.settings

    @QtCore.pyqtSlot()
    def initialize_spike_detection(self):
        if self.spike_mat is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText("")
            self.spike_detection_start_button.setEnabled(False)
            self.spike_detection_thread = SpikeDetectionThread(self, self.reader, self.settings.spike_window,
                                                               self.settings.mode, self.settings.threshold_factor)
            self.spike_detection_thread.progress_made.connect(self.on_progress_made)
            self.spike_detection_thread.operation_changed.connect(self.on_operation_changed)
            self.spike_detection_thread.channel_data_updated.connect(self.on_channel_data_updated)
            self.spike_detection_thread.single_spike_data_updated.connect(self.on_single_spike_data_updated)
            self.spike_detection_thread.finished.connect(self.on_spike_detection_thread_finished)

            debug_mode = False  # set to 'True' in order to debug plot creation with embed
            if debug_mode:
                # synchronous plotting (runs in main thread and thus allows debugging)
                self.spike_detection_thread.run()
            else:
                # asynchronous plotting (default):
                self.spike_detection_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately

            self.timer.start(2000) # time in [ms]

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
        self.timer.stop()
        self.progress_label.setText("Finished :)")
        if self.spike_detection_thread.spike_mat:
            self.spike_indices = self.spike_detection_thread.spike_indices.copy()
            self.spike_mat = self.spike_detection_thread.spike_mat.copy()
        self.spike_detection_thread = None
        self.spike_detection_start_button.setEnabled(True)
        if self.save_check_box.isChecked():
            self.save_spike_mat(self.spike_mat, self.spike_indices, self.reader.file_path)

    @QtCore.pyqtSlot(list)
    def on_single_spike_data_updated(self, data):
        signal, spike_time, spike_height, self.threshold = data[0], data[1], data[2], data[3]
        self.voltage_trace.append(signal)
        self.time_vt.append(list(np.arange(0, len(self.voltage_trace[-1]))/self.fs))
        # H, edges = np.histogram(signal, bins=1000)
        # centers = edges[:-1] + np.diff(edges)[0] / 2
        # self.signal_plot.setData(centers, H)
        self.spike_height.append([spike_height])
        self.spike_indices.append([spike_time/self.fs])

    @QtCore.pyqtSlot()
    def on_timer(self):
        if len(self.time_vt) == 0 or len(self.voltage_trace) == 0:
            return  # nothing to plot

        self.signal_plot.setData(self.time_vt[-1], self.voltage_trace[-1])
        self.hLine.setValue(self.threshold)
        self.hLine2.setValue(-1 * self.threshold)

        self.scatter.setData(self.spike_indices[-1], self.spike_height[-1])

    # function to save the found spiketimes stored in spike_mat as .csv file
    def save_spike_mat(self, spike_mat, spike_indices, mea_file):
        self.label_save_check_box.setText('saving spike times...')
        # take filepath and filename, to get name of mea file and save it to the same directory
        overall_path, filename = os.path.split(mea_file)
        if filename.endswith('.h5'):
            analysis_filename = filename[:-2] + 'meae'
        else:
            analysis_filename = filename
        analysis_file_path = os.path.join(overall_path, analysis_filename)
        if os.path.exists(analysis_file_path):
            with h5py.File(analysis_file_path, 'a') as hf:
                for idx, (spikes, indices) in enumerate(zip(spike_mat, spike_indices)):
                    spike_key = 'spiketimes_' + str(idx)
                    if spike_key in list(hf.keys()):
                        del hf[spike_key]
                        dset_4 = hf.create_dataset(spike_key, data=np.array(spikes))
                    else:
                        dset_4 = hf.create_dataset(spike_key, data=np.array(spikes))
                    indices_key = 'spiketimes_indices_' + str(idx)
                    if indices_key in list(hf.keys()):
                        del hf[indices_key]
                        dset_5 = hf.create_dataset(indices_key, data=np.array(indices))
                    else:
                        dset_5 = hf.create_dataset(indices_key, data=np.array(indices))
        else:
            with h5py.File(analysis_file_path, 'w') as hf:
                for idx, (spikes, indices) in enumerate(zip(spike_mat, spike_indices)):
                    spike_key = 'spiketimes_' + str(idx)
                    dset_4 = hf.create_dataset(spike_key, data=np.array(spikes))
                    indices_key = 'spiketimes_indices_' + str(idx)
                    dset_5 = hf.create_dataset(indices_key, data=np.array(indices))
        self.label_save_check_box.setText('spike times saved in: ' + analysis_file_path)

    # function to open spike_mat .csv in case it exists
    # def open_spikemat(self, filepath):
    #     with open(filepath, 'r') as read_obj:
    #         csv_reader = csv.reader(read_obj)
    #         spike_mat = list(csv_reader)
    #     return spike_mat

