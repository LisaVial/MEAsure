from PyQt5 import QtCore, QtWidgets, QtGui

from spike_detection_thread import SpikeDetectionThread

class SpikeDetectionWindow(QtWidgets.QDialog):
    def __init__(self, parent, mea_file, spike_mat):
        super().__init__(parent)

        self.mea_file = mea_file
        self.spike_mat = spike_mat

        title = 'Spike detection'
        self.setWindowTitle(title)

        self.spike_detection_thread = None

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        self.save_check_box = QtWidgets.QCheckBox("Save spiketimes")
        self.label_save_check_box = QtWidgets.QLabel("Don't save spiketimes")
        self.save_check_box.stateChanged.connect(self.save_check_box_clicked)

        main_layout.addWidget(self.save_check_box)

        self.spike_detection_start_button = QtWidgets.QPushButton(self)
        self.spike_detection_start_button.setText("Start spike detection")

        main_layout.addWidget(self.spike_detection_start_button)

        self.spike_detection_start_button.clicked.connect(self.initialize_spike_detection)

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

    def save_check_box_clicked(self):
        self.label_save_check_box.setText('Saving spikes to .csv file at the end of spike detection')

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

