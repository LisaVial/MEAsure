import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from filtering.filter_settings_widget import FilterSettingsWidget

class FilterSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, inital_settings=None):
        super().__init__(parent)

        title = 'Filtering'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.width = 300
        self.height = 200

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        self.filter_settings_widget = FilterSettingsWidget(self, inital_settings)
        main_layout.addWidget(self.filter_settings_widget)

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
        return self.filter_settings_widget.get_settings()

    def on_okay_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()