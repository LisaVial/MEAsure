from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

from mea_data_reader import MeaDataReader
from mea_grid import MeaGrid

from spike_detection.spike_detection_dialog import SpikeDetectionDialog
from filtering.filter_settings_dialog import FilterSettingsDialog
from filtering.filter_tab import FilterTab
from settings import Settings
from plot_dialog import PlotDialog


class MeaFileView(QtWidgets.QWidget):
    def __init__(self, parent, mea_file):
        super().__init__(parent)
        self.reader = MeaDataReader(mea_file)
        self.mea_file = mea_file

        self.filter_settings = Settings.instance.filter_settings

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
        sub_layout.addLayout(mea_grid_and_minor_widgets_layout)

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabBarAutoHide(False)

        sub_layout.addWidget(self.tab_widget)
        main_layout.addLayout(sub_layout)

    def on_show_mea_grid(self, is_pressed):
        self.mea_grid.setVisible(is_pressed)

    @QtCore.pyqtSlot()
    def open_sd_dialog(self):
        spike_detection_dialog = SpikeDetectionDialog(None, self.reader)
        spike_detection_dialog.exec_()

    @QtCore.pyqtSlot()
    def open_filter_dialog(self):
        settings_dialog = FilterSettingsDialog(self, self.filter_settings)
        if settings_dialog.exec() == 1:  # 'Execute' clicked
            self.filter_settings = settings_dialog.get_settings()
            # overwrite global settings as well
            Settings.instance.filter_settings = self.filter_settings

            # initialise filtering
            filter_tab = FilterTab(self, self.reader, self.filter_settings)
            self.tab_widget.addTab(filter_tab, "Filtering")
            filter_tab.initialize_filtering()


    @QtCore.pyqtSlot()
    def open_plot_dialog(self):
        plot_dialog = PlotDialog(None, self.reader)
        plot_dialog.exec_()

