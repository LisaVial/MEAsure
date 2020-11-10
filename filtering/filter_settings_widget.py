import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .filter_settings import FilterSettings


class FilterSettingsWidget(QtWidgets.QGroupBox):

    def __init__(self, parent, allowed_modes, settings=None):
        super().__init__(parent)

        self.setTitle("Settings")
        group_box_layout = QtWidgets.QGridLayout(self)

        valid_number_pattern = "[0-9]*\.{0,1][0-9]*"
        valid_number_regex = QtCore.QRegExp(valid_number_pattern)
        number_validator = QtGui.QRegExpValidator(valid_number_regex)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Which channels should be used?')

        group_layout = QtWidgets.QVBoxLayout(group_box)

        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        group_layout.addWidget(self.all_channels_button)

        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(FilterSettings.ChannelSelection.SELECTION in allowed_modes)
        group_layout.addWidget(self.selected_channels_button)

        group_box_layout.addWidget(group_box)

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

        self.save_filtered_traces_box = QtWidgets.QCheckBox('Save filtered traces')
        self.save_filtered_traces_label = QtWidgets.QLabel('')
        group_box_layout.addWidget(self.save_filtered_traces_box)
        group_box_layout.addWidget(self.save_filtered_traces_label)
        self.save_filtered_traces_box.stateChanged.connect(self.save_filtered_traces_changed)

        if not settings:
            # create default settings
            settings = FilterSettings()

        # initialise widgets with settings
        self.set_settings(settings)
        # update label (info about saving or not saving traces)
        self.save_filtered_traces_changed()

    def set_settings(self, settings):
        self.filter_combo_box.setCurrentIndex(settings.mode)
        self.single_cutoff_textbox.setText(str(settings.lower_cutoff))  # set entry index by reading mode (index) from settings
        self.second_cutoff_textbox.setText(str(settings.upper_cutoff))
        self.save_filtered_traces_box.setChecked(settings.save_filtered_traces)
        if settings.channel_selection == FilterSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == FilterSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

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

        settings.save_filtered_traces = self.save_filtered_traces_box.isChecked()
        settings.channel_selection = self.selected_channels_button.isChecked()

        return settings

    def save_filtered_traces_changed(self):
        if self.save_filtered_traces_box.isChecked():
            self.save_filtered_traces_label.setText("Saving filtered traces to .meae file at end of filtering")
        else:
            self.save_filtered_traces_label.setText("Don\'t save filtered traces")
