import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .filter_settings import FilterSettings


class FilterSettingsWidget(QtWidgets.QGroupBox):

    def __init__(self, parent, settings=None):
        super().__init__(parent)

        self.setTitle("Settings")
        group_box_layout = QtWidgets.QGridLayout(self)

        valid_number_pattern = "[0-9]*\.{0,1][0-9]*"
        valid_number_regex = QtCore.QRegExp(valid_number_pattern)
        number_validator = QtGui.QRegExpValidator(valid_number_regex)

        self.filter_combo_box = QtWidgets.QComboBox(self)

        self.filter_combo_box.addItem('Lowpass Filter')
        self.filter_combo_box.addItem('Highpass Filter')
        self.filter_combo_box.addItem('Bandpass Filter')

        self.filter_combo_box.setEditable(True)
        self.filter_combo_box.lineEdit().setReadOnly(True)

        self.filter_combo_box.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.filter_combo_box.currentIndexChanged.connect(self.filter_type_changed)
        group_box_layout.addWidget(self.filter_combo_box)

        self.single_cutoff_textbox = QtWidgets.QLineEdit(self)
        self.single_cutoff_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.textbox_label = QtWidgets.QLabel('Cutoff frequency [Hz]')
        group_box_layout.addWidget(self.single_cutoff_textbox)
        group_box_layout.addWidget(self.textbox_label)

        self.second_cutoff_textbox = QtWidgets.QLineEdit(self)
        self.second_cutoff_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.second_textbox_label = QtWidgets.QLabel('Upper cutoff frequency [Hz]')
        group_box_layout.addWidget(self.second_cutoff_textbox)
        group_box_layout.addWidget(self.second_textbox_label)
        self.second_cutoff_textbox.setVisible(False)
        self.second_textbox_label.setVisible(False)

        if not settings:
            # create default settings
            settings = FilterSettings()

        # initialise widgets with settings
        self.set_settings(settings)

    def set_settings(self, settings):
        self.filter_combo_box.setCurrentText(str(settings.mode))
        self.single_cutoff_textbox.setText(str(settings.lower_cutoff))  # set entry index by reading mode (index) from settings
        self.second_cutoff_textbox.setText(str(settings.upper_cutoff))

    def filter_type_changed(self, index):
        self.filter_combo_box.setCurrentIndex(index)
        if index == 2:
            self.textbox_label.setText('Lower cutoff frequency [Hz]')
            self.second_cutoff_textbox.setVisible(True)
            self.second_textbox_label.setVisible(True)

    def get_settings(self):
        settings = FilterSettings()
        # get settings by reading current values

        try:
            settings.lower_cutoff = float(self.single_cutoff_textbox.text())
        except ValueError:
            # not a float
            pass

        settings.mode = self.filter_combo_box.currentIndex()

        try:
            settings.upper_cutoff = float(self.second_cutoff_textbox.text())
        except ValueError:
            # not a float
            pass

        return settings

