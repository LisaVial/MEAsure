from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5 import QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import numpy as np


button_style = """
QPushButton {
    background-color: #9ec2c8;
    border-radius: 13;
    border: 0.5px solid black
}

QPushButton:checked {
    background-color: #006d7c;
    color: white
}

QPushButton:hover {
    background-color: #FFFFFF;
}
"""


class MeaGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.grid_table = QTableWidget(self)
        self.grid_table.setRowCount(16)
        self.grid_table.setColumnCount(16)
        self.grid_table.horizontalHeader().setVisible(False)
        self.grid_table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.grid_table)

        mcs_channel_ids_file = open(r'/home/lisa_ruth/PycharmProjects/Spielwiese/ch_ids.txt', 'r')
        self.ch_ids = mcs_channel_ids_file.read().split(', ')
        self.all_channel_indices = np.array([int(v) for v in self.ch_ids if v != ''])
        self.labels = []
        self.label_indices_map = dict()
        for col, c in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R']):
            for row, n in enumerate(range(1, 17)):
                if c == 'A' and n == 1 or c == 'A' and n == 16 or c == 'R' and n == 1 or c == 'R' and n == 16:
                    self.grid_table.setColumnWidth(col, 35)
                    self.grid_table.setItem(row, col, QTableWidgetItem(''))
                    self.grid_table.item(row, col).setFlags(QtCore.Qt.NoItemFlags)
                    continue

                number_str = str(n)
                self.labels.append(c + number_str)
                # if n < 10:
                #     number_str = "0" + number_str
                label = (c + number_str)

                self.grid_table.setColumnWidth(col, 35)
                self.grid_table.setItem(row, col, QTableWidgetItem(label))

                # creation of dictionary
                id = c + str(n)

                self.label_indices_map[id] = {}
                if col == 0:
                    self.label_indices_map[id]['grid index'] = self.all_channel_indices[row - 1]
                elif col != 0 and col != 15:
                    self.label_indices_map[id]['grid index'] = self.all_channel_indices[row + (col*16) - 2]
                else:
                    self.label_indices_map[id]['grid index'] = self.all_channel_indices[row + (col*16) - 3]

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)

    def get_selected_channels(self):
        selected_channels = []
        for item in self.grid_table.selectedItems():
            label = item.text()
            selected_channels.append((label, self.label_indices_map[label]['grid index']))

        return selected_channels

    def select_all(self):
        self.grid_table.selectAll()

    def select_none(self):
        self.grid_table.clearSelection()

    def invert_selection(self):
        for row in range(self.grid_table.rowCount()):
            for column in range(self.grid_table.columnCount()):
                is_selected = self.grid_table.item(row, column).isSelected()
                self.grid_table.item(row, column).setSelected(not is_selected)

    def are_all_selected(self):
        channel_count = len(self.labels)
        return len(self.grid_table.selectedItems()) == channel_count

    def is_none_selected(self):
        return len(self.grid_table.selectedItems()) == 0

    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_context_menu(self, point):
        menu = QtWidgets.QMenu(self)

        select_all_action = QtWidgets.QAction("Select All")
        select_all_action.triggered.connect(self.select_all)
        select_all_action.setEnabled(not self.are_all_selected())
        menu.addAction(select_all_action)

        select_none_action = QtWidgets.QAction("Select None")
        select_none_action.triggered.connect(self.select_none)
        select_none_action.setEnabled(not self.is_none_selected())
        menu.addAction(select_none_action)

        invert_selection_action = QtWidgets.QAction("Invert Selection")
        invert_selection_action.triggered.connect(self.invert_selection)
        menu.addAction(invert_selection_action)

        menu.exec(self.mapToGlobal(point))
