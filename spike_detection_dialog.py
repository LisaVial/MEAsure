from PyQt5 import QtCore, QtWidgets, QtGui
import csv
import os

from spike_detection_thread import SpikeDetectionThread


class SpikeDetectionDialog(QtWidgets.QDialog):
    def __init__(self, parent, mea_file):
        super().__init__(parent)

        # set variables that come from MEA file reader as class variables
        self.mea_file = mea_file
        self.spike_mat = None

        # basic layout of the new spike_detection_dialog
        title = 'Spike detection'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
        self.resize(800, 600)

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
        self.label_save_check_box = QtWidgets.QLabel("Don't save spiketimes")
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
        main_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        main_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        self.spike_mat = None

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

    def check_for_spike_times_csv(self):
        # scan path of current file, if there is a .csv file
        spiketimes_csv = self.mea_file[:-3] + '_spiketimes.csv'
        if os.path.exists(spiketimes_csv):
            # if this file already exists, set it as spike_mat
            spike_mat = self.open_spikemat(spiketimes_csv)
            # show user an answer that informs him/her about the file and asks, if the user wants to detect spikes again
            # anyways
            answer = QtWidgets.QMessageBox.information(self, 'spiketimes already found', 'Detect spikes again?',
                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                              QtWidgets.QMessageBox.No)
            # depending on the answer of the user, set the found csv file as spike_mat or set spike_mat to none
            if answer == QtWidgets.QMessageBox.Yes:
                return None
            else:
                return spike_mat
        # in case there is no csv file found, the spike_mat stays none
        else:
            return None

    def save_check_box_clicked(self):
        # change label of the save check box in case the user clicked it
        self.label_save_check_box.setText('Saving spikes to .csv file at the end of spike detection')

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
            self.spike_mat = self.spike_detection_thread.spike_mat.copy()
        self.spike_detection_thread = None
        self.spike_detection_button.setEnabled(True)
        if self.save_check_box.isChecked():
            self.save_spike_mat(self.spike_mat, self.mea_file + '_spiketimes.csv')

    # function to save the found spiketimes stored in spike_mat as .csv file
    def save_spike_mat(self, spike_mat, mea_file):
        self.label_save_check_box.setText('saving spike times...')
        # take filepath and filename, to get name of mea file and save it to the same directory
        file_name = mea_file[:-3]
        spike_filename = file_name + '_spiketimes.csv'
        self.save_spikemat(spike_mat, spike_filename)
        self.label_save_check_box.setText('spike times saved in: ' + spike_filename)

    # function to open spike_mat .csv in case it exists
    def open_spikemat(self, filepath):
        with open(filepath, 'r') as read_obj:
            csv_reader = csv.reader(read_obj)
            spike_mat = list(csv_reader)
        return spike_mat

