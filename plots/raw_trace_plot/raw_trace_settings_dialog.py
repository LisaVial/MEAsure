from PyQt5 import QtCore, QtWidgets

from plots.raw_trace_plot.raw_trace_settings import RawTraceSettings


class RawTraceSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_selection_mode, settings=None):
        super().___init__(parent)

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

    def get_settings(self):
        settings = RawTraceSettings()
        settings.channel_selection = self.selected_channels_button.isChecked()
        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()