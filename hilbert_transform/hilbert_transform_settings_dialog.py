import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from hilbert_transform.hilbert_transform_settings import HilbertTransformSettings

class HilbertTransformSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, allowed_channel_modes):
        super().__init__(parent)

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
        main_layout.addWidget(group_box)

        self.okay_button = QtWidgets.QPushButton(self)
        self.okay_button.setText('Execute')
        self.okay_button.clicked.connect(self.on_okay_clicked)
        main_layout.addWidget(self.okay_button)

        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText('Abort')
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        main_layout.addWidget(self.cancel_button)