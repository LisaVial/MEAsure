from PyQt5 import QtCore, QtWidgets

from plots.raw_trace_plot.raw_trace_settings import RawTraceSettings
from utility.hilbert_time_widget import HilbertTimeWidget


class RawTraceSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_selection_mode, duration, settings=None):
        super().__init__(parent)
        self.mea_file_view = parent
        self.duration = duration

        title = 'Raw traces'

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
        self.selected_channels_button.setEnabled(RawTraceSettings.ChannelSelection.SELECTION in
                                                 allowed_channel_selection_mode)

        group_layout.addWidget(self.selected_channels_button)
        main_layout.addWidget(group_box)

        self.time_zero_textbox = QtWidgets.QLineEdit(self)
        self.time_zero_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.time_zero_textbox_label = QtWidgets.QLabel('Start time of plot:')
        main_layout.addWidget(self.time_zero_textbox)
        main_layout.addWidget(self.time_zero_textbox_label)

        self.time_one_textbox = QtWidgets.QLineEdit(self)
        self.time_one_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.time_one_textbox_label = QtWidgets.QLabel('End time of plot:')
        main_layout.addWidget(self.time_one_textbox)
        main_layout.addWidget(self.time_one_textbox_label)

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
            settings = RawTraceSettings()

        if not settings.is_end_time_initialised:
            settings.end_time = int(self.duration)
            settings.is_end_time_initialised = True

        self.set_settings(settings)

    def set_settings(self, settings):
        self.time_zero_textbox.setText(str(settings.start_time))
        self.time_one_textbox.setText(str(settings.end_time))
        if settings.channel_selection == RawTraceSettings.ChannelSelection.ALL:
            self.all_channels_button.setChecked(True)
        elif settings.channel_selection == RawTraceSettings.ChannelSelection.SELECTION:
            self.selected_channels_button.setChecked(True)

    def get_settings(self):
        settings = RawTraceSettings()
        settings.channel_selection = self.selected_channels_button.isChecked()
        settings.start_time = int(self.time_zero_textbox.text())
        settings.end_time = int(self.time_one_textbox.text())
        settings.channel_time_selection = self.hilbert_time_widget.get_channel_time_selection()
        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()