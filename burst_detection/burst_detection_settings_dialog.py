from PyQt5 import QtCore, QtWidgets

from burst_detection.burst_detection_settings import BurstDetectionSettings


class BurstDetectionSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_selection_mode, settings=None):
        super().__init__(parent)
        title = 'Burst Detection Settings'

        self.allowed_channel_modes = allowed_channel_selection_mode
        self.settings = settings

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Which channels should be used?')

        group_layout = QtWidgets.QVBoxLayout(group_box)

        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        group_layout.addWidget(self.all_channels_button)

        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(BurstDetectionSettings.ChannelSelection.SELECTION
                                                 in self.allowed_channel_modes)
        group_layout.addWidget(self.selected_channels_button)

        self.min_spikes_per_burst_textbox = QtWidgets.QLineEdit(self)
        self.min_spikes_per_burst_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.min_spikes_per_burst_textbox_label = QtWidgets.QLabel('minimum # of spikes per burst')
        group_layout.addWidget(self.min_spikes_per_burst_textbox)
        group_layout.addWidget(self.min_spikes_per_burst_textbox_label)

        self.max_time_diff_textbox = QtWidgets.QLineEdit(self)
        self.max_time_diff_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.max_time_diff_textbox_label = QtWidgets.QLabel('maximum time difference between spikes')
        group_layout.addWidget(self.max_time_diff_textbox)
        group_layout.addWidget(self.max_time_diff_textbox_label)

        main_layout.addWidget(group_box)

        self.okay_button = QtWidgets.QPushButton(self)
        self.okay_button.setText('Execute')
        self.okay_button.clicked.connect(self.on_okay_clicked)
        main_layout.addWidget(self.okay_button)

        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText('Abort')
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        main_layout.addWidget(self.cancel_button)

        self.setWindowTitle(title)

        if not settings:
            settings = BurstDetectionSettings()

        self.apply_settings(settings)

    def apply_settings(self, settings):
        if self.settings is not None:
            if BurstDetectionSettings.ChannelSelection.SELECTION in self.allowed_channel_modes:
                self.selected_channels_button.setChecked(True)
            else:
                self.all_channels_button.setChecked(True)
            self.min_spikes_per_burst_textbox.setText(str(self.settings.min_spikes_per_burst))
            self.max_time_diff_textbox.setText(str(self.settings.max_spike_time_diff))

    def get_settings(self):
        if self.settings is None:
            settings = BurstDetectionSettings()
        if self.selected_channels_button.isChecked():
            self.settings.channel_selection = BurstDetectionSettings.ChannelSelection.SELECTION
        else:
            self.settings.channel_selection = BurstDetectionSettings.ChannelSelection.ALL
        self.settings.min_spikes_per_burst = int(self.min_spikes_per_burst_textbox.text())
        self.settings.max_spike_time_diff = float(self.max_time_diff_textbox.text())

        return self.settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()
