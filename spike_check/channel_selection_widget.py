from PyQt5 import QtWidgets, QtCore
from utility.channel_utility import ChannelUtility


class ChannelSelectionWidget(QtWidgets.QWidget):

    channel_selection_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        main_layout = QtWidgets.QHBoxLayout(self)

        channel_labels = ChannelUtility.get_channel_labels()
        self.channel_selection_combobox = QtWidgets.QComboBox(self)
        self.channel_selection_combobox.setEditable(True)
        line_edit = self.channel_selection_combobox.lineEdit()
        line_edit.setReadOnly(True)
        line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.channel_selection_combobox.addItems(channel_labels)
        for i in range(self.channel_selection_combobox.count()):
            self.channel_selection_combobox.setItemData(i, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)
        self.label = self.channel_selection_combobox.itemText(0)
        self.channel_selection_combobox.currentIndexChanged.connect(self.channel_selection_change)
        main_layout.addWidget(self.channel_selection_combobox)

    @QtCore.pyqtSlot(int)
    def channel_selection_change(self, index):
        self.label = self.channel_selection_combobox.itemText(index)
        self.channel_selection_changed.emit(self.label)
