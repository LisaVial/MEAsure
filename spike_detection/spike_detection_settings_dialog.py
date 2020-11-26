from PyQt5 import QtCore, QtWidgets, QtGui

from spike_detection.spike_detection_settings_widget import SpikeDetectionSettingsWidget


class SpikeDetectionSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_file_modes, allowed_modes, inital_settings=None):
        super().__init__(parent)

        # basic layout of the new spike_detection_dialog
        title = 'Spike detection'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
        self.width = 400
        self.height = 200

        # main layout is the layout for this specific dialog, sub layouts can also be defined and later on be added to
        # the main layout (e.g. if single buttons/plots/whatever should have a defined layout)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.spike_detection_settings_widget = SpikeDetectionSettingsWidget(self, allowed_file_modes,
                                                                            allowed_modes, inital_settings)
        main_layout.addWidget(self.spike_detection_settings_widget)

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
        return self.spike_detection_settings_widget.get_settings()

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()


