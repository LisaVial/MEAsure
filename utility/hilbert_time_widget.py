import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .customize_hilbert_times_dialog import CustomizeHilbertTimesDialog

import results


class HilbertTimeWidget(QtWidgets.QGroupBox):

    def __init__(self, parent, result_storing: results.ResultStoring, channel_time_selection: dict,
                 is_checked: bool = True):
        super().__init__(parent)

        self.result_storing = result_storing
        if len(channel_time_selection.keys()) > 0:
            self.channel_time_selection = channel_time_selection
        else:
            # initialise by selecting first variant for each label
            self.channel_time_selection = dict()
            for label in self.result_storing.get_hilbert_transform_data_dict().keys():
                self.channel_time_selection[label] = self.result_storing.get_hilbert_transform_data_variations(label)[0]

        self.setTitle("Use times determined in Hilbert transformation")
        self.setCheckable(True)

        group_box_layout = QtWidgets.QVBoxLayout(self)

        self.customize_button = QtWidgets.QPushButton("Customize...")
        self.customize_button.pressed.connect(self.on_customize_button_pressed)
        group_box_layout.addWidget(self.customize_button)

        has_data = result_storing.has_hilbert_transform_data()
        if has_data:
            self.setChecked(is_checked)
        else:
            # no data -> hide and disable widget
            self.setVisible(False)
            self.setEnabled(False)

    def on_customize_button_pressed(self):
        dialog = CustomizeHilbertTimesDialog(self, self.result_storing, self.channel_time_selection)
        if dialog.exec() == 1:
            # selection confirmed
            self.channel_time_selection = dialog.get_channel_time_selection()

    def get_channel_time_selection(self):
        return self.channel_time_selection.copy()


