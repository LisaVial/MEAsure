from PyQt5 import QtCore, QtWidgets
from results import ResultStoring


class CustomizeHilbertTimesDialog(QtWidgets.QDialog):

    def __init__(self, parent, result_storing: ResultStoring, channel_time_selection: dict):
        super().__init__(parent)
        self.result_storing = result_storing

        main_layout = QtWidgets.QHBoxLayout(self)

        time_selection_dict = result_storing.get_hilbert_transform_data_dict()

        channel_time_selection_layout = QtWidgets.QGridLayout()
        current_layout_row = 0
        self.time_selection_widget_dict = dict()

        for label in sorted(time_selection_dict.keys()):
            if len(time_selection_dict[label]) > 1:
                channel_time_selection_layout.addWidget(QtWidgets.QLabel(label), current_layout_row, 0)
                selection_widget = QtWidgets.QComboBox(self)

                current_time_range = None
                if label in channel_time_selection.keys():
                    current_time_range = channel_time_selection[label]

                current_index = 0
                for index, time_range in enumerate(time_selection_dict[label]):
                    selection_widget.addItem(str(time_range[0]) + ' - ' + str(time_range[1]))

                    if time_range == current_time_range:
                        current_index = index

                selection_widget.setCurrentIndex(current_index)
                channel_time_selection_layout.addWidget(selection_widget, current_layout_row, 1)
                self.time_selection_widget_dict[label] = selection_widget
                current_layout_row += 1

        other_channels_text = "No selection possible or necessary for other channels"
        channel_time_selection_layout.addWidget(QtWidgets.QLabel(other_channels_text), current_layout_row, 0, 1, 2)
        main_layout.addLayout(channel_time_selection_layout)

        button_pane_layout = QtWidgets.QVBoxLayout()
        button_pane_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        ok_button = QtWidgets.QPushButton('OK')
        ok_button.pressed.connect(self.on_ok_button_pressed)
        button_pane_layout.addWidget(ok_button)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.pressed.connect(self.on_cancel_button_pressed)
        button_pane_layout.addWidget(cancel_button)
        main_layout.addLayout(button_pane_layout)

    def get_channel_time_selection(self):
        channel_time_selection = dict()

        for label in sorted(self.time_selection_widget_dict.keys()):
            selection_widget = self.time_selection_widget_dict[label]
            selection_index = selection_widget.currentIndex()
            selected_time_range = self.result_storing.get_hilbert_transform_data_variations(label)[selection_index]
            channel_time_selection[label] = selected_time_range

        return channel_time_selection

    def on_ok_button_pressed(self):
        self.accept()

    def on_cancel_button_pressed(self):
        self.reject()
