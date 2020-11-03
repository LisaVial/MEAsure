import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .rasterplot_settings import RasterplotSettings


class RasterplotSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_modes, settings=None):
        super().__init__(parent)
        title = 'Settings'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.width = 300
        self.height = 200

        self.setWindowTitle(title)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        group_box = QtWidgets.QGroupBox(self)
        group_box.setTitle('Select a file for plot:')

        group_layout = QtWidgets.QVBoxLayout(group_box)

        self.mcs_file_button = QtWidgets.QRadioButton('MCS file')
        self.mcs_file_button.setEnabled(RasterplotSettings.Mode.MCS in allowed_modes)
        group_layout.addWidget(self.mcs_file_button)

        self.meae_file_button = QtWidgets.QRadioButton('MEAE file')
        self.meae_file_button.setEnabled(RasterplotSettings.Mode.MEAE in allowed_modes)
        group_layout.addWidget(self.meae_file_button)

        self.sc_file_button = QtWidgets.QRadioButton('SC file')
        self.sc_file_button.setEnabled(RasterplotSettings.Mode.SC in allowed_modes)
        group_layout.addWidget(self.sc_file_button)

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
            settings = RasterplotSettings()

        initial_mode = RasterplotSettings.Mode.MCS
        if settings.mode in allowed_modes:
            initial_mode = settings.mode

        # initialise widgets with settings
        self.set_settings(settings)

    def set_settings(self, settings):
        if settings.mode == RasterplotSettings.Mode.MCS:
            self.mcs_file_button.setChecked(True)
        elif settings.mode == RasterplotSettings.Mode.MEAE:
            self.meae_file_button.setChecked(True)
        elif settings.mode == RasterplotSettings.Mode.SC:
            self.sc_file_button.setChecked(True)

    def get_settings(self):
        settings = RasterplotSettings()
        if self.mcs_file_button.isChecked():
            settings.mode = RasterplotSettings.Mode.MCS
        elif self.meae_file_button.isChecked():
            settings.mode = RasterplotSettings.Mode.MEAE
        elif self.sc_file_button.isChecked():
            settings.mode = RasterplotSettings.Mode.SC

        return settings

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()