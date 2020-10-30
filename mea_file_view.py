from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

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
        self.show_mea_grid.setCheckable(True)
        self.show_mea_grid.setChecked(True)
        self.toolbar.addAction(self.show_mea_grid)

        self.show_filter_dialog = QtWidgets.QAction("Filtering", self)
        self.show_filter_dialog.triggered.connect(self.open_filter_dialog)
        self.toolbar.addAction(self.show_filter_dialog)

        self.show_spike_detection_dialog = QtWidgets.QAction('Spike Detection', self)
        self.show_spike_detection_dialog.triggered.connect(self.open_sd_dialog)
        self.toolbar.addAction(self.show_spike_detection_dialog)

        main_layout.addWidget(self.toolbar)

        sub_layout = QtWidgets.QHBoxLayout(self)
        sub_layout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        mea_grid_and_minor_widgets_layout = QtWidgets.QVBoxLayout(self)
        mea_grid_and_minor_widgets_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.mea_grid = MeaGrid(self)
        self.mea_grid.setFixedSize(600, 600)
        mea_grid_and_minor_widgets_layout.addWidget(self.mea_grid)

        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far...')
        mea_grid_and_minor_widgets_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        mea_grid_and_minor_widgets_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFixedSize(600, 26)
        self.progress_bar.setTextVisible(True)
        mea_grid_and_minor_widgets_layout.addWidget(self.progress_bar)

        sub_layout.addLayout(mea_grid_and_minor_widgets_layout)

        self.plot_widget = pg.plot(title='Live plots')
        self.plot_widget.setBackground('w')
        styles = {'color': 'k', 'font-size': '10px'}

        sub_layout.addWidget(self.plot_widget)
        main_layout.addLayout(sub_layout)

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

