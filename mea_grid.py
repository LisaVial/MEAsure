from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets


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

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(2)
        self.grid_layout.setVerticalSpacing(0)

        self.label_button_map = dict()
        self.labels = []
        self.label_indices_map = dict()
        for col, c in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R']):
            for row, n in enumerate(range(1, 17)):
                if c == 'A' and n == 1 or c == 'A' and n == 16 or c == 'R' and n == 1 or c == 'R' and n == 16:
                    continue

                number_str = str(n)
                self.labels.append(c + number_str)
                if n < 10:
                    number_str = "0" + number_str
                label = (c + number_str)

                button = QPushButton(c + str(n))
                button.setFixedSize(26, 26)
                button.setStyleSheet(button_style)
                button.setCheckable(True)
                button.setChecked(False)
                id = c + str(n)

                # creation of dictionary

                self.label_indices_map[id] = {}
                if col == 0:
                    self.label_indices_map[id]['grid index'] = row - 1
                elif col != 0 and col != 15:
                    self.label_indices_map[id]['grid index'] = row + (col*16) - 2
                else:
                    self.label_indices_map[id]['grid index'] = row + (col*16) - 3

                self.label_button_map[label] = button
                self.grid_layout.addWidget(button, row, col)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)

    def get_selected_channels(self):
        ordered_labels = list(self.label_button_map.keys())
        ordered_labels.sort()

        selected_channels = []
        for idx, label in enumerate(ordered_labels):
            if self.label_button_map[label].isChecked():
                selected_channels.append((self.labels[idx], self.label_indices_map[self.labels[idx]]['grid index']))
        print(selected_channels)
        return selected_channels

    def select_all(self):
        for label in self.label_button_map.keys():
            self.label_button_map[label].setChecked(True)

    def select_none(self):
        for label in self.label_button_map.keys():
            self.label_button_map[label].setChecked(False)

    def invert_selection(self):
        for label in self.label_button_map.keys():
            is_checked = self.label_button_map[label].isChecked()
            self.label_button_map[label].setChecked(not is_checked)

    def are_all_selected(self):
        channel_count = len(self.label_button_map.keys())
        return (len(self.get_selected_channels()) == channel_count)

    def is_none_selected(self):
        return (len(self.get_selected_channels()) == 0)

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
