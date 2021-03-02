from PyQt5 import QtWidgets, QtCore


class ChannelSelectionWidget(QtWidgets.QWidget):

    channel_selection_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        main_layout = QtWidgets.QHBoxLayout(self)

        channel_labels = self.get_channel_labels()
        self.channel_selection_combobox = QtWidgets.QComboBox(self)
        self.channel_selection_combobox.setEditable(True)
        line_edit = self.channel_selection_combobox.lineEdit()
        line_edit.setReadOnly(True)
        line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.channel_selection_combobox.addItems(channel_labels)
        # ToDo: get other labels aligned at center as well
        for i in range(self.channel_selection_combobox.count()):
            self.channel_selection_combobox.setItemData(i, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)
        self.label = self.channel_selection_combobox.itemText(0)
        self.channel_selection_combobox.currentIndexChanged.connect(self.channel_selection_change)
        main_layout.addWidget(self.channel_selection_combobox)

    @QtCore.pyqtSlot(int)
    def channel_selection_change(self, index):
        self.label = self.channel_selection_combobox.itemText(index)
        self.channel_selection_changed.emit(self.label)

    @staticmethod
    def get_channel_labels():
        labels = []
        for col, c in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R']):
            for row, n in enumerate(range(1, 17)):
                if c == 'A' and n == 1 or c == 'A' and n == 16 or c == 'R' and n == 1 or c == 'R' and n == 16:
                    continue
                number_str = str(n)
                labels.append(c + number_str)
        return labels
