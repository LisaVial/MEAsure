from PyQt5 import QtCore, QtWidgets


class FilterDialog(QtWidgets.QDialog):
    def __init__(self, parent, mea_file):
        super().__init__(parent)

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

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter)
        self.setWindowTitle(title)

        self.filter_settings_layout = QtWidgets.QStackedLayout()
        self.filter_settings_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.filter_settings_label = QtWidgets.QLabel('Filter settings')
        self.filter_settings_layout.addWidget(self.filter_settings_label)
        main_layout.addLayout(self.filter_settings_layout)

        self.filter_combo_box = QtWidgets.QComboBox(self)
        self.filter_combo_box.setFixedSize(self.width, 25)
        self.filter_combo_box.addItem('Lowpass Filter')
        self.filter_combo_box.addItem('Highpass Filter')
        self.filter_combo_box.addItem('Bandpass Filter')
        self.filter_combo_box.addItem('Notch Filter')
        self.filter_combo_box.setEditable(True)
        self.filter_combo_box.lineEdit().setReadOnly(True)
        self.filter_combo_box.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.filter_combo_box.currentIndexChanged.connect(self.filter_type_changed)
        self.filter_settings_layout.addWidget(self.filter_combo_box)
        self.filter_settings_layout.setCurrentIndex(1)

        self.single_cutoff_textbox = QtWidgets.QLineEdit(self)
        self.textbox_label = QtWidgets.QLabel('Cutoff frequency [Hz]')
        self.filter_settings_layout.addWidget(self.single_cutoff_textbox)
        self.filter_settings_layout.addWidget(self.textbox_label)
        self.second_cutoff_textbox = QtWidgets.QLineEdit(self)
        self.second_textbox_label = QtWidgets.QLabel('Upper cutoff frequency [Hz]')
        self.filter_settings_layout.addWidget(self.second_cutoff_textbox)
        self.filter_settings_layout.addWidget(self.second_textbox_label)

        self.save_filtered_box = QtWidgets.QCheckBox('Save filtered traces')
        self.label_save_filtered_box = QtWidgets.QLabel('Dont save filtered traces')
        main_layout.addWidget(self.save_filtered_box)
        main_layout.addWidget(self.label_save_filtered_box)
        self.save_filtered_box.stateChanged.connect(self.save_filtered_box_clicked)

        self.filter_start_button = QtWidgets.QPushButton(self)
        self.filter_start_button.setText('Start filtering')
        self.filter_start_button.clicked.connect(self.initialize_filtering)
        main_layout.addWidget(self.filter_start_button)

        self.operation_label = QtWidgets.QLabel(self)
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

    def save_filtered_box_clicked(self):
        self.label_save_filtered_box.setText('Saving filtered traces to .h5 file at end of filtering')

    def initialize_filtering(self):
        pass

    # this function changes the label of the progress bar to inform the user what happens in the backgound
    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    # this function updates the progress bar
    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")
