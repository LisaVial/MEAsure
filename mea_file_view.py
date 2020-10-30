from PyQt5 import QtWidgets, QtCore
import os

from plot_widget import PlotWidget
from mea_data_reader import MeaDataReader
from mea_grid import MeaGrid

from spike_detection_dialog import SpikeDetectionDialog
from filter_dialog import FilterDialog
from plot_dialog import PlotDialog


class MeaFileView(QtWidgets.QWidget):
    def __init__(self, parent, mea_file):
        super().__init__(parent)
        self.reader = MeaDataReader(mea_file)
        self.mea_file = mea_file

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.toolbar = QtWidgets.QToolBar(self)

        self.show_mea_grid = QtWidgets.QAction("MEA grid", self)
        self.show_mea_grid.triggered.connect(self.on_show_mea_grid)
        self.show_mea_grid.setCheckable(True)  # kann an/aus sein
        self.show_mea_grid.setChecked(True)
        self.toolbar.addAction(self.show_mea_grid)

        self.show_filter_dialog = QtWidgets.QAction("Filtering", self)
        self.show_filter_dialog.triggered.connect(self.open_filter_dialog)
        self.toolbar.addAction(self.show_filter_dialog)

        main_layout.addWidget(self.toolbar)

        self.mea_grid = MeaGrid(self)
        self.mea_grid.setFixedSize(500, 500)

        grid_buttons_and_progress_bar_layout = QtWidgets.QHBoxLayout(self)
        grid_buttons_and_progress_bar_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        grid_buttons_and_progress_bar_layout.addWidget(self.mea_grid)


        self.spike_detection_dialog_button = QtWidgets.QPushButton(self)
        self.spike_detection_dialog_button.setText("Open spike detection dialog")
        self.spike_detection_dialog_button.clicked.connect(self.open_sd_dialog)
        grid_buttons_and_progress_bar_layout.addWidget(self.spike_detection_dialog_button)

        self.plot_button = QtWidgets.QPushButton(self)
        self.plot_button.setText("Plots")
        self.plot_button.clicked.connect(self.open_plot_dialog)

        grid_buttons_and_progress_bar_layout.addWidget(self.plot_button)

        self.operation_label = QtWidgets.QLabel(self)
        grid_buttons_and_progress_bar_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        grid_buttons_and_progress_bar_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        grid_buttons_and_progress_bar_layout.addWidget(self.progress_bar)
        main_layout.addLayout(grid_buttons_and_progress_bar_layout)

    def on_show_mea_grid(self, is_pressed):
        self.mea_grid.setVisible(is_pressed)

    @QtCore.pyqtSlot()
    def open_sd_dialog(self):
        spike_detection_dialog = SpikeDetectionDialog(None, self.reader)
        spike_detection_dialog.exec_()

    @QtCore.pyqtSlot()
    def open_filter_dialog(self):
        filter_dialog = FilterDialog(None, self.reader)
        filter_dialog.exec_()

    @QtCore.pyqtSlot()
    def open_plot_dialog(self):
        plot_dialog = PlotDialog(None, self.reader)
        plot_dialog.exec_()

    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")

