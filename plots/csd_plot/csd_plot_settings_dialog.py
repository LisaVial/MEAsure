from PyQt5 import QtCore, QtWidgets

from .csd_plot_settings import CsdPlotSettings


class CsdPlotSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_modes, settings=None):
        super().__init__(parent)
        title = 'Settings'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)

        self.setWindowTitle(title)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Which channels should be used?')

        channel_selection_group_layout = QtWidgets.QVBoxLayout(group_box)

        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        channel_selection_group_layout.addWidget(self.all_channels_button)

        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(CsdPlotSettings.ChannelSelection.SELECTION in allowed_channel_modes)
        channel_selection_group_layout.addWidget(self.selected_channels_button)
        main_layout.addWidget(group_box)

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
            settings = CsdPlotSettings()

        # initialise widgets with settings
        self.set_settings(settings)

    def set_settings(self, settings):
        if settings.channel_selection == CsdPlotSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == CsdPlotSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

    def get_settings(self):
        settings = CsdPlotSettings()
        settings.channel_selection = self.selected_channels_button.isChecked()
        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()
