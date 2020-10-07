import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .spike_detection_settings import SpikeDetectionSettings


class SpikeDetectionSettingsWidget(QtWidgets.QGroupBox):

    def __init__(self, parent, settings=None):
        super().__init__(parent)

        self.setTitle("Settings")
        group_box_layout = QtWidgets.QGridLayout(self)

        # create validator in order to make sure only valid numbers can be entered in specific input fields
        valid_number_pattern = "[0-9]*\.{0,1}[0-9]*"
        valid_number_regex = QtCore.QRegExp(valid_number_pattern)
        number_validator = QtGui.QRegExpValidator(valid_number_regex)

        # add spike window input field
        self.spike_window_input = QtWidgets.QLineEdit(self)
        self.spike_window_input.setValidator(number_validator)  # set number validator (see above)
        group_box_layout.addWidget(QtWidgets.QLabel("Spike window in [s]"), 0, 0)
        group_box_layout.addWidget(self.spike_window_input, 0, 1)

        # add mode selection widget
        self.mode_widget = QtWidgets.QComboBox(self)
        self.mode_widget.setEditable(False)  # do not allow entering text
        self.mode_widget.addItems(["Peaks", "Troughs", "Both"])  # items have to be in same order as in Mode definition
        group_box_layout.addWidget(QtWidgets.QLabel("Mode"), 1, 0)
        group_box_layout.addWidget(self.mode_widget, 1, 1)

        # add threshold factor input field
        self.threshold_factor_input = QtWidgets.QLineEdit(self)
        self.threshold_factor_input.setValidator(number_validator)  # set number validator (see above)
        group_box_layout.addWidget(QtWidgets.QLabel("Threshold factor"), 2, 0)
        group_box_layout.addWidget(self.threshold_factor_input, 2, 1)

        if not settings:
            # create default settings
            settings = SpikeDetectionSettings()

        # initialise widgets with settings
        self.set_settings(settings)

    def set_settings(self, settings):
        self.spike_window_input.setText(str(settings.spike_window))
        self.mode_widget.setCurrentIndex(settings.mode)  # set entry index by reading mode (index) from settings
        self.threshold_factor_input.setText(str(settings.threshold_factor))

    def get_settings(self):
        settings = SpikeDetectionSettings()
        # get settings by reading current values

        try:
            settings.spike_window = float(self.spike_window_input.text())
        except ValueError:
            # not a float
            pass

        settings.mode = self.mode_widget.currentIndex()

        try:
            settings.threshold_factor = float(self.threshold_factor_input.text())
        except ValueError:
            # not a float
            pass

        return settings
