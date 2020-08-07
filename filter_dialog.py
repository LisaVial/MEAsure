from PyQt5 import QtCore, QtWidgets
import h5py
import os

from filter_thread import FilterThread


class FilterDialog(QtWidgets.QDialog):
    def __init__(self, parent, plot_widget, mea_file):
        super().__init__(parent)
        self.plot_widget = plot_widget
        self.mea_file = mea_file
        self.filtered_mat = None

        title = 'Filtering'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)

        self.filtering_thread = None
        self.filter_mat = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.setWindowTitle(title)

        self.filter_combo_box = QtWidgets.QComboBox(self)
        self.filter_combo_box.setFixedSize(self.width, 25)
        self.filter_combo_box.addItem('Lowpass Filter')
        self.filter_combo_box.addItem('Highpass Filter')
        # self.filter_combo_box.addItem('Notch Filter')
        self.filter_combo_box.addItem('Bandpass Filter')
        self.filter_combo_box.setEditable(True)
        self.filter_combo_box.lineEdit().setReadOnly(True)
        self.filter_combo_box.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.filter_combo_box.currentIndexChanged.connect(self.filter_type_changed)
        main_layout.addWidget(self.filter_combo_box)

        self.single_cutoff_textbox = QtWidgets.QLineEdit(self)
        self.textbox_label = QtWidgets.QLabel('Cutoff frequency [Hz]')
        main_layout.addWidget(self.single_cutoff_textbox)
        main_layout.addWidget(self.textbox_label)
        self.second_cutoff_textbox = QtWidgets.QLineEdit(self)
        self.second_textbox_label = QtWidgets.QLabel('Upper cutoff frequency [Hz]')
        main_layout.addWidget(self.second_cutoff_textbox)
        main_layout.addWidget(self.second_textbox_label)
        self.second_cutoff_textbox.setVisible(False)
        self.second_textbox_label.setVisible(False)

        self.save_filtered_box = QtWidgets.QCheckBox('Save filtered traces')
        self.label_save_filtered_box = QtWidgets.QLabel('Don\'t save filtered traces')
        main_layout.addWidget(self.save_filtered_box)
        main_layout.addWidget(self.label_save_filtered_box)
        self.save_filtered_box.stateChanged.connect(self.save_filtered_box_clicked)

        self.filter_start_button = QtWidgets.QPushButton(self)
        self.filter_start_button.setText('Start filtering')
        self.filter_start_button.clicked.connect(self.initialize_filtering)
        main_layout.addWidget(self.filter_start_button)

        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far')
        main_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        main_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

    def filter_type_changed(self, index):
        self.filter_combo_box.setCurrentIndex(index)
        if index == 2:
            self.textbox_label.setText('Lower cutoff frequency [Hz]')
            self.second_cutoff_textbox.setVisible(True)
            self.second_textbox_label.setVisible(True)

    def save_filtered_box_clicked(self):
        self.label_save_filtered_box.setText('Saving filtered traces to .h5 file at end of filtering')

    def initialize_filtering(self):
        filter_mode = self.filter_combo_box.currentIndex()
        cutoff_1 = float(self.single_cutoff_textbox.text())
        cutoff_2 = None
        if self.filter_combo_box.currentIndex() == 2:
            cutoff_2 = float(self.second_cutoff_textbox.text())
        if self.filter_mat is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('Filtering')
            self.filter_start_button.setEnabled(False)
            self.filtering_thread = FilterThread(self, self.plot_widget, self.mea_file, filter_mode, cutoff_1, cutoff_2)
            self.filtering_thread.progress_made.connect(self.on_progress_made)
            self.filtering_thread.operation_changed.connect(self.on_operation_changed)

            debug_mode = False  # set to 'True' in order to debug plot creation with embed
            if debug_mode:
                # synchronous plotting (runs in main thread and thus allows debugging)
                self.filtering_thread.run()
            else:
                # asynchronous plotting (default):
                self.filtering_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately

    def on_filter_thread_finished(self):
        self.progress_label.setText('Finished :)')
        if self.filtering_thread.filtered_mat:
            self.filter_mat = self.filtering_thread.filtered_mat.copy()
        self.filtering_thread = None
        self.filter_start_button.setEnabled(True)
        print(self.mea_file[:-3] + '_filtered.h5')
        if self.save_filtered_box.isChecked():
            self.save_filter_mat(self.filter_mat, self.mea_file[:-3] + '_filtered.h5')

    def save_filter_mat(self, filter_mat, filename):
        print(filename)
        with h5py.File(filename, 'w') as hf:
            hf.create_dataset('filter', data=filter_mat)
        self.label_save_filtered_box.setText('Filtered traces saved in: ' + filename)

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

    # this function changes the label of the progress bar to inform the user what happens in the background
    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    # this function updates the progress bar
    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")
