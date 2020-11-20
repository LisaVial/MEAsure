import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .filter_settings import FilterSettings


class FilterSettingsWidget(QtWidgets.QGroupBox):
    """
    The FilterSettingsWidget object is a QGroupBox, which allows you to show single widgets in multiple rows and
    columns. This object sets up most of the widgets, which are shown in the FilterSettingsDialog.
    """
    # Like before, first we set up the class and tell it, which other class is its parent.
    def __init__(self, parent, allowed_modes, settings=None):
        super().__init__(parent)

        # Now, we set up the title of the widget and its layout.
        self.setTitle("Settings")
        group_box_layout = QtWidgets.QGridLayout(self)

        # Since the user will be allowed to write something, we have to tell which type of input is allowed.
        valid_number_pattern = "[0-9]*\.{0,1][0-9]*"
        valid_number_regex = QtCore.QRegExp(valid_number_pattern)
        number_validator = QtGui.QRegExpValidator(valid_number_regex)

        # Here, a GroupBox widget is generated
        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Which channels should be used?')

        # group_layout has the same function as the main_layout in scripts setting up dialogs.
        group_layout = QtWidgets.QVBoxLayout(group_box)

        # Creation of a RadioButton (round, checkable button). This first button is for the case, that all MEA channels
        # will be filtered and is set to default.
        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        group_layout.addWidget(self.all_channels_button)

        # Creation of a RadioButton. The second button is only checkable if the user has clicked on several channels in
        # the MeaGrid.
        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(FilterSettings.ChannelSelection.SELECTION in allowed_modes)
        group_layout.addWidget(self.selected_channels_button)

        group_box_layout.addWidget(group_box)

        # Here, a QComboBox (drop down menu) is created. With this, the user can choose which filter type will be used.
        self.filter_combo_box = QtWidgets.QComboBox(self)

        # With the next three lines, new entries for the drop down menu are created and in the brackets, it is defined
        # which text is assigned to their entry and shown to the user.
        self.filter_combo_box.addItem('Lowpass Filter')
        self.filter_combo_box.addItem('Highpass Filter')
        self.filter_combo_box.addItem('Bandpass Filter')

        # Line 56 - 58 were a little trick to be able to set the alignment of the texts to centered.
        self.filter_combo_box.setEditable(True)
        self.filter_combo_box.lineEdit().setReadOnly(True)
        self.filter_combo_box.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

        # Here, the selection of an entry in the drop down menu is linked to a function which handles the different
        # cases of different selected filter modes.
        self.filter_combo_box.currentIndexChanged.connect(self.filter_type_changed)
        group_box_layout.addWidget(self.filter_combo_box)

        # Depending on the chosen filter mode a QLineEdit (blank slot for the user to type in things) is shown or not.
        # First they have to be created and if they will be shown or not is handled by the filter_type_changed function.
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
        # In line 79 and 80 the second_cutoff_textbox is hidden and once the bandpass filter is selected, it will be
        # set visible.
        self.second_cutoff_textbox.setVisible(False)
        self.second_textbox_label.setVisible(False)

        # This last widget handles the information whether or not the filtered traces should be stored to a new
        # .h5 at the end of the filtering process.
        # todo: think of a widget to enable the user to set the name of the saved .h5 file
        self.save_filtered_traces_box = QtWidgets.QCheckBox('Save filtered traces')
        self.save_filtered_traces_label = QtWidgets.QLabel('')
        group_box_layout.addWidget(self.save_filtered_traces_box)
        group_box_layout.addWidget(self.save_filtered_traces_label)
        self.save_filtered_traces_box.stateChanged.connect(self.save_filtered_traces_changed)

        # if there are no changes in the settings the default settings are used
        if not settings:
            # create default settings
            settings = FilterSettings()

        # Here, the widgets are initialized with settings
        self.set_settings(settings)
        # This function updates the label (info about saving or not saving traces).
        self.save_filtered_traces_changed()

    def set_settings(self, settings):
        """
        :param settings: default or changed FilterSettings
        :return: This function changes the GUI output according to the settings (which widgets will be shown)
        """
        # Set entry index by reading mode (index) from settings.
        self.filter_combo_box.setCurrentIndex(settings.mode)
        # Set text of cutoff line edits according to cutoffs from settings
        self.single_cutoff_textbox.setText(str(settings.lower_cutoff))
        self.second_cutoff_textbox.setText(str(settings.upper_cutoff))
        # Set checked state of check box for saving filtered traces from settings.
        self.save_filtered_traces_box.setChecked(settings.save_filtered_traces)
        # Set if all or only a few channels will be filtered from settings.
        if settings.channel_selection == FilterSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == FilterSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

    def filter_type_changed(self, index):
        """
        :param index: index is the signal PyQt emits, depending on which drop down menu entry of the combo_box is
        selected by the user
        :return: visibility of second cutoff frequency line edit for the user to change the entry
        """
        self.filter_combo_box.setCurrentIndex(index)
        if index == 2:
            self.textbox_label.setText('Lower cutoff frequency [Hz]')
            self.second_cutoff_textbox.setVisible(True)
            self.second_textbox_label.setVisible(True)

    def get_settings(self):
        """
        This function loads the settings from the filter_settings.py script and stores them in variables for this class.
        :return: settings
        """
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
        """
        This function handles the label of the checkbox which handles saving of filtered traces. In the dialog it is
        only needed to change the label, the consequences are handled by the settings.
        :return:
        """
        if self.save_filtered_traces_box.isChecked():
            self.save_filtered_traces_label.setText("Saving filtered traces to .meae file at end of filtering")
        else:
            self.save_filtered_traces_label.setText("Don\'t save filtered traces")
