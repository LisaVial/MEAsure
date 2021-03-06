from PyQt5 import QtCore, QtWidgets

from .isi_histogram_settings import IsiHistogramSettings


class IsiHistogramSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_modes, allowed_channel_modes, settings=None):
        super().__init__(parent)
        title = 'Settings'
        self.setWindowTitle(title)

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Select a file for plot:')

        group_layout = QtWidgets.QVBoxLayout(group_box)

        self.mcs_file_button = QtWidgets.QRadioButton('MCS file')
        self.mcs_file_button.setEnabled(IsiHistogramSettings.Mode.MCS in allowed_modes)
        group_layout.addWidget(self.mcs_file_button)

        self.meae_file_button = QtWidgets.QRadioButton('MEAE file')
        self.meae_file_button.setEnabled(IsiHistogramSettings.Mode.MEAE in allowed_modes)
        group_layout.addWidget(self.meae_file_button)

        self.sc_file_button = QtWidgets.QRadioButton('SC file')
        self.sc_file_button.setEnabled(IsiHistogramSettings.Mode.SC in allowed_modes)
        group_layout.addWidget(self.sc_file_button)

        main_layout.addWidget(group_box)

        channel_selection_group_box = QtWidgets.QGroupBox(self)
        channel_selection_group_box.setTitle('Which channels should be used?')

        channel_selection_group_layout = QtWidgets.QVBoxLayout(channel_selection_group_box)

        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        channel_selection_group_layout.addWidget(self.all_channels_button)

        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(IsiHistogramSettings.ChannelSelection.SELECTION in
                                                 allowed_channel_modes)
        channel_selection_group_layout.addWidget(self.selected_channels_button)

        main_layout.addWidget(channel_selection_group_box)

        self.okay_button = QtWidgets.QPushButton(self)
        self.okay_button.setText('Execute')
        self.okay_button.clicked.connect(self.on_okay_clicked)
        main_layout.addWidget(self.okay_button)

        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText('Abort')
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        main_layout.addWidget(self.cancel_button)

        if not settings:
            # create default settings
            settings = IsiHistogramSettings()

        initial_mode = IsiHistogramSettings.Mode.MCS
        if settings.mode in allowed_modes:
            initial_mode = settings.mode

        # initialise widgets with settings
        self.set_settings(settings)

    def set_settings(self, settings):
        if settings.mode == IsiHistogramSettings.Mode.MCS:
            self.mcs_file_button.setChecked(True)
        elif settings.mode == IsiHistogramSettings.Mode.MEAE:
            self.meae_file_button.setChecked(True)
        elif settings.mode == IsiHistogramSettings.Mode.SC:
            self.sc_file_button.setChecked(True)

        if settings.channel_selection == IsiHistogramSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == IsiHistogramSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

    def get_settings(self):
        settings = IsiHistogramSettings()
        if self.mcs_file_button.isChecked():
            settings.mode = IsiHistogramSettings.Mode.MCS
        elif self.meae_file_button.isChecked():
            settings.mode = IsiHistogramSettings.Mode.MEAE
        elif self.sc_file_button.isChecked():
            settings.mode = IsiHistogramSettings.Mode.SC
        settings.channel_selection = self.selected_channels_button.isChecked()

        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()

