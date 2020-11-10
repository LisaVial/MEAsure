import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .spike_detection_settings import SpikeDetectionSettings


class SpikeDetectionSettingsWidget(QtWidgets.QGroupBox):

    def __init__(self, parent, allowed_modes, settings=None):
        super().__init__(parent)

        self.setTitle("Settings")
        group_box_layout = QtWidgets.QGridLayout(self)

        # create validator in order to make sure only valid numbers can be entered in specific input fields
        valid_number_pattern = "[0-9]*\.{0,1}[0-9]*"
        valid_number_regex = QtCore.QRegExp(valid_number_pattern)
        number_validator = QtGui.QRegExpValidator(valid_number_regex)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Which channels should be used?')

        group_layout = QtWidgets.QVBoxLayout(group_box)

        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        group_layout.addWidget(self.all_channels_button)

        # To Do: implement allowed modes before opening settings dialog
        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(SpikeDetectionSettings.ChannelSelection.SELECTION in allowed_modes)
        group_layout.addWidget(self.selected_channels_button)

        group_box_layout.addWidget(group_box, 0, 0, 1, 2)

        # add spike window input field
        self.spike_window_input = QtWidgets.QLineEdit(self)
        self.spike_window_input.setValidator(number_validator)  # set number validator (see above)
        group_box_layout.addWidget(QtWidgets.QLabel("Spike window in [s]"), 1, 0)
        group_box_layout.addWidget(self.spike_window_input, 1, 1)

        # add mode selection widget
        self.mode_widget = QtWidgets.QComboBox(self)
        self.mode_widget.setEditable(False)  # do not allow entering text
        self.mode_widget.addItems(["Peaks", "Troughs", "Both"])  # items have to be in same order as in Mode definition
        group_box_layout.addWidget(QtWidgets.QLabel("Mode"), 2, 0)
        group_box_layout.addWidget(self.mode_widget, 2, 1)

        # add threshold factor input field
        self.threshold_factor_input = QtWidgets.QLineEdit(self)
        self.threshold_factor_input.setValidator(number_validator)  # set number validator (see above)
        group_box_layout.addWidget(QtWidgets.QLabel("Threshold factor"), 3, 0)
        group_box_layout.addWidget(self.threshold_factor_input, 3, 1)

        self.save_spiketimes_box = QtWidgets.QCheckBox('Save filtered traces')
        self.save_spiketimes_label = QtWidgets.QLabel('')
        group_box_layout.addWidget(self.save_spiketimes_box)
        group_box_layout.addWidget(self.save_spiketimes_label)
        self.save_spiketimes_box.stateChanged.connect(self.save_spiketimes_changed)

        if not settings:
            # create default settings
            settings = SpikeDetectionSettings()

        # initialise widgets with settings
        self.set_settings(settings)
        # update label (info about saving or not saving traces)
        self.save_spiketimes_changed()

    def set_settings(self, settings):
        self.spike_window_input.setText(str(settings.spike_window))
        self.mode_widget.setCurrentIndex(settings.mode)  # set entry index by reading mode (index) from settings
        self.threshold_factor_input.setText(str(settings.threshold_factor))
        self.save_spiketimes_box.setChecked(settings.save_spiketimes)
        if settings.channel_selection == SpikeDetectionSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == SpikeDetectionSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

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
        settings.save_filtered_traces = self.save_spiketimes_box.isChecked()
        settings.channel_selection = self.selected_channels_button.isChecked()
        return settings

    def save_spiketimes_changed(self):
        if self.save_spiketimes_box.isChecked():
            self.save_spiketimes_label.setText("Saving spiketimes to .meae file at the end of filtering")
        else:
            self.save_spiketimes_label.setText("Don\'t save spiketimes")