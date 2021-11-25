import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from hilbert_transform.hilbert_transform_settings import HilbertTransformSettings


class HilbertTransformSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_modes, initial_settings=None):
        super().__init__(parent)
        self.allowed_channel_modes = allowed_channel_modes
        self.settings = initial_settings

        title = 'Hilbert Transform'
        self.setWindowTitle(title)

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)

        width = 400
        height = 400
        self.setFixedSize(width, height)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Which channels should be used?')

        group_layout = QtWidgets.QVBoxLayout(group_box)
        self.all_channels_button = QtWidgets.QRadioButton('all MEA channels')
        group_layout.addWidget(self.all_channels_button)

        self.selected_channels_button = QtWidgets.QRadioButton('only selected channels')
        self.selected_channels_button.setEnabled(HilbertTransformSettings.ChannelSelection.SELECTION in
                                                 allowed_channel_modes)
        group_layout.addWidget(self.selected_channels_button)

        self.threshhold_factor_textbox = QtWidgets.QLineEdit(self)
        self.threshhold_factor_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.threshhold_factor_textbox_label = QtWidgets.QLabel('threshold factor')
        group_layout.addWidget(self.threshhold_factor_textbox)
        group_layout.addWidget(self.threshhold_factor_textbox_label)

        self.min_peaks_per_seizure_textbox = QtWidgets.QLineEdit(self)
        self.min_peaks_per_seizure_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.min_peaks_per_seizure_textbox_label = \
            QtWidgets.QLabel('minimum # of peaks')
        group_layout.addWidget(self.min_peaks_per_seizure_textbox)
        group_layout.addWidget(self.min_peaks_per_seizure_textbox_label)
        main_layout.addWidget(group_box)

        self.okay_button = QtWidgets.QPushButton(self)
        self.okay_button.setText('Execute')
        self.okay_button.clicked.connect(self.on_okay_clicked)
        main_layout.addWidget(self.okay_button)

        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText('Abort')
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        main_layout.addWidget(self.cancel_button)

        self.apply_settings()

    def apply_settings(self):
        if self.settings is not None:
            if HilbertTransformSettings.ChannelSelection.SELECTION in self.allowed_channel_modes:
                self.selected_channels_button.setChecked(True)
            else:
                self.all_channels_button.setChecked(True)

            self.threshhold_factor_textbox.setText(str(self.settings.threshold_factor))
            self.min_peaks_per_seizure_textbox.setText(str(self.settings.min_peaks_per_seizure))

    def get_settings(self):
        if self.settings is None:
            self.settings = HilbertTransformSettings()

        if self.selected_channels_button.isChecked():
            self.settings.channel_selection = HilbertTransformSettings.ChannelSelection.SELECTION
        else:
            self.settings.channel_selection = HilbertTransformSettings.ChannelSelection.ALL

        self.settings.threshold_factor = int(self.threshhold_factor_textbox.text())
        self.settings.min_peaks_per_seizure = int(self.min_peaks_per_seizure_textbox.text())
        return self.settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()
