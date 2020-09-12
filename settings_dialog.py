from PyQt5 import QtCore, QtWidgets
import h5py
import os
import numpy as np

from spike_detection.spike_detection_settings_widget import SpikeDetectionSettingsWidget


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, initial_settings=None):
        super().__init__(parent)

        title = 'Settings'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.width = 300
        self.height = 200
        self.resize(self.width, self.height)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        self.spike_detection_settings_widget = SpikeDetectionSettingsWidget(self, initial_settings)
        main_layout.addWidget(self.spike_detection_settings_widget)

        self.okay_button = QtWidgets.QPushButton(self)
        self.okay_button.setText('Okay')
        self.okay_button.clicked.connect(self.on_ok_clicked)
        main_layout.addWidget(self.okay_button)

        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        main_layout.addWidget(self.cancel_button)

        self.setWindowTitle(title)

    def get_settings(self):
        return self.spike_detection_settings_widget.get_settings()

    def on_ok_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()