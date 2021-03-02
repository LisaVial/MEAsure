from PyQt5 import QtWidgets, QtCore


class NavigationButtonsWidget(QtWidgets.QWidget):
    def __init__(self, parent, max_idx):
        super().__init__(parent)

        buttons_layout = QtWidgets.QHBoxLayout(self)

        # ToDo: implement max_index by getting total length of spiketimes found for respective channel
        self.max_index = max_idx
        self.index = 0

        self.previous_button = QtWidgets.QPushButton(self)
        self.previous_button.setText("<")
        self.previous_button.pressed.connect(self.on_previous_button_pressed)

        self.next_button = QtWidgets.QPushButton(self)
        self.next_button.setText(">")
        self.next_button.pressed.connect(self.on_next_button_pressed)

        buttons_layout.addWidget(self.previous_button)
        buttons_layout.addWidget(self.next_button)

    @QtCore.pyqtSlot()
    def on_previous_button_pressed(self):
        self.index -= 1
        self.previous_button.setEnabled(self.index > 0)
        self.next_button.setEnabled(self.index < self.max_index - 1)

    @QtCore.pyqtSlot()
    def on_next_button_pressed(self):
        self.index += 1
        self.previous_button.setEnabled(self.index > 0)
        self.next_button.setEnabled(self.index < self.max_index - 1)


