from PyQt5 import QtCore, QtWidgets

from frequency_bands_analysis.frequency_bands_analysis_settings import FrequencyBandsAnalysisSettings

from utility.hilbert_time_widget import HilbertTimeWidget


class FrequencyBandsAnalysisSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_selection_mode, settings=None):
        super().__init__(parent)
        self.mea_file_view = parent
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
        is_channel_selection_allowed = (FrequencyBandsAnalysisSettings.ChannelSelection.SELECTION in
                                        allowed_channel_selection_mode)
        self.selected_channels_button.setEnabled(is_channel_selection_allowed)
        group_layout.addWidget(self.selected_channels_button)

        self.all_channels_button.setChecked(not is_channel_selection_allowed)
        self.selected_channels_button.setChecked(is_channel_selection_allowed)

        main_layout.addWidget(group_box)

        analysis_selection_group_box = QtWidgets.QGroupBox(self)
        analysis_selection_group_box.setTitle('What do you want to analyse?')

        analysis_selection_layout = QtWidgets.QVBoxLayout(analysis_selection_group_box)

        self.ictal_activity_button = QtWidgets.QRadioButton('analyse ictal activity')
        analysis_selection_layout.addWidget(self.ictal_activity_button)
        self.ictal_activity_button.setChecked(True)

        self.csd_activity_button = QtWidgets.QRadioButton('analyse CSD data')
        analysis_selection_layout.addWidget(self.csd_activity_button)

        main_layout.addWidget(analysis_selection_group_box)

        channel_time_selection = dict()
        if settings is not None:
            channel_time_selection = settings.channel_time_selection

        self.hilbert_time_widget = HilbertTimeWidget(self, self.mea_file_view.results, channel_time_selection)
        main_layout.addWidget(self.hilbert_time_widget)

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
            settings = FrequencyBandsAnalysisSettings()

        self.set_settings(settings)

    def set_settings(self, settings):
        if settings.channel_selection == FrequencyBandsAnalysisSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == FrequencyBandsAnalysisSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

    def get_settings(self):
        settings = FrequencyBandsAnalysisSettings()
        settings.channel_selection = self.selected_channels_button.isChecked()
        if self.ictal_activity_button.isChecked():
            settings.analysis_mode = 0
        elif self.csd_activity_button.isChecked():
            settings.analysis_mode = 1
        settings.channel_time_selection = self.hilbert_time_widget.get_channel_time_selection()
        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()
