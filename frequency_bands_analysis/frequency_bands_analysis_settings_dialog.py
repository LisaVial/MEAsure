from PyQt5 import QtCore, QtWidgets

from frequency_bands_analysis.frequency_bands_analysis_settings import FrequencyBandsAnalysisSettings

from IPython import embed


class FrequencyBandsAnalysisSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_selection_mode, initial_settings=None):
        super().__init__(parent)

        title = 'Frequency bands analysis'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)

        main_layout = QtWidgets.QGridLayout(self)
        # main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Which channels should be used?')

        group_layout = QtWidgets.QVBoxLayout(group_box)

        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        group_layout.addWidget(self.all_channels_button)

        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(FrequencyBandsAnalysisSettings.ChannelSelection.SELECTION in
                                                 allowed_channel_selection_mode)
        group_layout.addWidget(self.selected_channels_button)
        main_layout.addWidget(group_box)

        analysis_selection_group_box = QtWidgets.QGroupBox(self)
        analysis_selection_group_box.setTitle('What do you want to analyse?')

        analysis_selection_layout = QtWidgets.QVBoxLayout(analysis_selection_group_box)

        self.ictal_activity_button = QtWidgets.QRadioButton('analyse ictal activity')
        analysis_selection_layout.addWidget(self.ictal_activity_button)

        self.csd_activity_button = QtWidgets.QRadioButton('analyse CSD data')
        analysis_selection_layout.addWidget(self.csd_activity_button)

        main_layout.addWidget(analysis_selection_group_box)

        self.okay_button = QtWidgets.QPushButton(self)
        self.okay_button.setText('Execute')
        self.okay_button.clicked.connect(self.on_okay_clicked)
        main_layout.addWidget(self.okay_button)

        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText('Abort')
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        main_layout.addWidget(self.cancel_button)

        self.setWindowTitle(title)

    def get_settings(self):
        settings = FrequencyBandsAnalysisSettings()
        settings.channel_selection = self.selected_channels_button.isChecked()
        if self.ictal_activity_button.isChecked():
            settings.analysis_mode = 0
        elif self.csd_activity_button.isChecked():
            settings.analysis_mode = 1
        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()
