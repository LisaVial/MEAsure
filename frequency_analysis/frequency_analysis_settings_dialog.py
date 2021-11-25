from PyQt5 import QtCore, QtWidgets

from frequency_analysis.frequency_analysis_settings import FrequencyAnalysisSettings
from utility.hilbert_time_widget import HilbertTimeWidget


class FrequencyAnalysisSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_selection_mode, settings=None):
        super().__init__(parent)
        self.mea_file_view = parent
        title = 'Frequency Analysis'

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

        # To Do: implement allowed modes before opening settings dialog
        self.selected_channels_button = QtWidgets.QRadioButton('only selected MEA channels')
        self.selected_channels_button.setEnabled(FrequencyAnalysisSettings.ChannelSelection.SELECTION in
                                                 allowed_channel_selection_mode)
        group_layout.addWidget(self.selected_channels_button)
        main_layout.addWidget(group_box)

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
            settings = FrequencyAnalysisSettings()

        self.set_settings(settings)

    def set_settings(self, settings):
        if settings.channel_selection == FrequencyAnalysisSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == FrequencyAnalysisSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

    def get_settings(self):
        settings = FrequencyAnalysisSettings()
        settings.channel_selection = self.selected_channels_button.isChecked()
        settings.channel_time_selection = self.hilbert_time_widget.get_channel_time_selection()
        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()