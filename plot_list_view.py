from PyQt5 import QtCore, QtWidgets
import os

from plot_manager import PlotManager


class PlotListView(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.plot_manager = PlotManager.instance

        self.plots = []
        self.plot_list = QtWidgets.QListWidget(self)

        self.save_button = QtWidgets.QPushButton('Save checked plots')
        self.save_button.setFixedHeight(32)
        self.save_button.pressed.connect(self.on_save_button_pressed)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        main_layout.addWidget(self.plot_list)
        main_layout.addWidget(self.save_button)

    def add_plot(self):
        self.plots.append(self.plot_manager.get_plots())
        # figure out how to get appropriate plot names
        new_item = QtWidgets.QListWidgetItem(self.plot_manager.plot_names)
        new_item.setCheckState(QtCore.Qt.Unchecked)
        self.plot_list.addItem(new_item)

    def on_save_button_pressed(self):
        self.save_button.setEnabled(False)
        selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Please chose a directory.")
        if len(selected_folder) > 0:
            plots_to_save = self.get_checked_plots()
            for plot in plots_to_save:
                filename = os.path.join(selected_folder, plot.plot_name + '.png')
                plot.figure.savefig(filename)
        self.save_button.setEnabled(True)

    def get_checked_plots(self):
        checked_plots = []
        for index in range(self.plot_list.count()):
            item = self.plot_list.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checked_plots.append(self.plots[index])
        return checked_plots
