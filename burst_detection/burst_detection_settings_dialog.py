from PyQt5 import QtCore, QtWidgets

from burst_detection_settings import BurstDetectionSettings

class BurstDetectionSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowd_channel_selection_mode, settings=None):
        super().__init__(parent)
        title = 'Burst Detection Settings'

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
                                                 in allowd_channel_selection_mode)
        group_layout.addWidget(self.selected_channels_button)
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

        self.set_settings(settings)

    def set_settings(self, settings):
        if settings.channel_selection == BurstDetectionSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == BurstDetectionSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

    def get_settings(self):
        settings = BurstDetectionSettings()
        settings.channel_selection = self.selected_channels_button.isChecked()
        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()
