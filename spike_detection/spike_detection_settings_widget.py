import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .spike_detection_settings import SpikeDetectionSettings


class SpikeDetectionSettingsWidget(QtWidgets.QGroupBox):

    def __init__(self, parent, allowed_file_modes, allowed_modes, mea_file_exists, meae_path, settings=None):
        super().__init__(parent)

        self.setTitle("Settings")
        main_layout = QtWidgets.QGridLayout(self)

        # create validator in order to make sure only valid numbers can be entered in specific input fields
        valid_number_pattern = "[0-9]*\.{0,1}[0-9]*"
        valid_number_regex = QtCore.QRegExp(valid_number_pattern)
        number_validator = QtGui.QRegExpValidator(valid_number_regex)

        group_box_file_mode = QtWidgets.QGroupBox(self)
        group_box_file_mode.setTitle('Select a file for plot:')

        group_layout_file_mode = QtWidgets.QVBoxLayout(group_box_file_mode)

        self.mea_file_exists = mea_file_exists
        self.meae_path = meae_path

        self.mcs_file_button = QtWidgets.QRadioButton('MCS file')
        self.mcs_file_button.setEnabled(SpikeDetectionSettings.FileMode.MCS in allowed_file_modes)
        group_layout_file_mode.addWidget(self.mcs_file_button)

        self.meae_file_button = QtWidgets.QRadioButton('MEAE file')
        self.meae_file_button.setEnabled(SpikeDetectionSettings.FileMode.MEAE in allowed_file_modes)
        group_layout_file_mode.addWidget(self.meae_file_button)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Which channels should be used?')

        group_layout = QtWidgets.QVBoxLayout(group_box)
        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        group_layout.addWidget(self.all_channels_button)

        # To Do: implement allowed modes before opening settings dialog
        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(SpikeDetectionSettings.ChannelSelection.SELECTION in allowed_modes)
        group_layout.addWidget(self.selected_channels_button)

        main_layout.addWidget(group_box_file_mode, 0, 0, 1, 2)
        main_layout.addWidget(group_box, 1, 0, 1, 2)

        # add spike window input field
        self.spike_window_input = QtWidgets.QLineEdit(self)
        self.spike_window_input.setValidator(number_validator)  # set number validator (see above)
        main_layout.addWidget(QtWidgets.QLabel("Spike window in [s]"), 2, 0)
        main_layout.addWidget(self.spike_window_input, 2, 1)

        # add mode selection widget
        self.mode_widget = QtWidgets.QComboBox(self)
        self.mode_widget.setEditable(False)  # do not allow entering text
        self.mode_widget.addItems(["Peaks", "Troughs", "Both"])  # items have to be in same order as in Mode definition
        main_layout.addWidget(QtWidgets.QLabel("Mode"), 3, 0)
        main_layout.addWidget(self.mode_widget, 3, 1)

        # add threshold factor input field
        self.threshold_factor_input = QtWidgets.QLineEdit(self)
        self.threshold_factor_input.setValidator(number_validator)  # set number validator (see above)
        main_layout.addWidget(QtWidgets.QLabel("Threshold factor"), 4, 0)
        main_layout.addWidget(self.threshold_factor_input, 4, 1)

        self.save_spiketimes_box = QtWidgets.QCheckBox('Save filtered traces')
        main_layout.addWidget(self.save_spiketimes_box, 5, 0)
        self.save_spiketimes_label = QtWidgets.QLabel('')
        self.get_existing_file_box = QtWidgets.QCheckBox('Append to existing file')
        self.get_existing_file_box.setVisible(False)
        self.get_existing_file_box.stateChanged.connect(self.get_existing_file_box_changed)
        main_layout.addWidget(self.get_existing_file_box, 6, 0)
        self.filename_entry_label = QtWidgets.QLabel(self)
        self.filename_entry_label.setVisible(False)
        self.filename_entry_label.setText('Enter filename without extension:')
        self.filename_entry = QtWidgets.QLineEdit(self)
        self.filename_entry.setVisible(False)
        main_layout.addWidget(self.filename_entry_label, 7, 0)
        main_layout.addWidget(self.filename_entry, 7, 1)
        main_layout.addWidget(self.save_spiketimes_label, 8, 0)
        self.save_spiketimes_box.stateChanged.connect(self.save_spiketimes_changed)

        if not settings:
            # create default settings
            settings = SpikeDetectionSettings()

        # initialise widgets with settings
        self.set_settings(settings)
        # update label (info about saving or not saving traces)
        self.save_spiketimes_changed()

    def set_settings(self, settings):
        if settings.file_mode == SpikeDetectionSettings.FileMode.MCS:
            self.mcs_file_button.setChecked(True)
        elif settings.file_mode == SpikeDetectionSettings.FileMode.MEAE:
            self.meae_file_button.setChecked(True)
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
        if self.mcs_file_button.isChecked():
            settings.file_mode = SpikeDetectionSettings.FileMode.MCS
        elif self.meae_file_button.isChecked():
            settings.file_mode = SpikeDetectionSettings.FileMode.MEAE

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
        settings.save_spiketimes = self.save_spiketimes_box.isChecked()
        settings.append_to_file = self.get_existing_file_box.isChecked()
        settings.channel_selection = self.selected_channels_button.isChecked()
        return settings

    def get_meae_filename(self):
        return self.filename_entry.text().strip()

    def get_existing_file_box_changed(self):
        if self.get_existing_file_box.isChecked():
            self.filename_entry_label.setVisible(False)
            self.filename_entry.setVisible(False)

    def save_spiketimes_changed(self):
        if self.save_spiketimes_box.isChecked():
            self.get_existing_file_box.setVisible(True)
            if self.mea_file_exists:
                self.get_existing_file_box.setCheckable(True)
            else:
                self.get_existing_file_box.setCheckable(False)
            self.filename_entry_label.setVisible(True)
            self.filename_entry.setVisible(True)
            self.save_spiketimes_label.setText("Saving spiketimesto .meae file at end of spike detection")

        else:
            self.get_existing_file_box.setVisible(False)
            self.filename_entry_label.setVisible(False)
            self.filename_entry.setVisible(False)
            self.save_spiketimes_label.setText("Don\'t save spiketimes")