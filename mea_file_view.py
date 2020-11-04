from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

from mcs_data_reader import McsDataReader
from meae_data_reader import MeaeDataReader
from SC_data_reader import SCDataReader

from mea_grid import MeaGrid

from settings import Settings
from file_manager import FileManager

from spike_detection.spike_detection_dialog import SpikeDetectionDialog

from filtering.filter_settings_dialog import FilterSettingsDialog
from filtering.filter_tab import FilterTab

from plots.csd_plot_tab import CsdPlotTab

from plots.raster_plot.rasterplot_tab import RasterplotTab
from plots.heatmap.heatmap_tab import HeatmapTab

from plots.plot_settings_dialog import PlotSettingsDialog
from plots.plot_settings import PlotSettings


class MeaFileView(QtWidgets.QWidget):
    def __init__(self, parent, mea_file):
        super().__init__(parent)
        self.reader = McsDataReader(mea_file)
        self.mea_file = mea_file

        self.filter_settings = Settings.instance.filter_settings
        self.plot_settings = Settings.instance.plot_settings

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.toolbar = QtWidgets.QToolBar(self)

        self.show_file_manager = QtWidgets.QAction("File manager", self)
        self.show_file_manager.triggered.connect(self.on_show_file_manager)
        self.show_file_manager.setCheckable(True)
        self.show_file_manager.setChecked(False)
        self.toolbar.addAction(self.show_file_manager)

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

        self.add_csd_plot_tab = QtWidgets.QAction('CSD plot', self)
        self.add_csd_plot_tab.triggered.connect(self.add_csd_plot_to_tabs)
        self.toolbar.addAction(self.add_csd_plot_tab)

        self.add_rasterplot_tab = QtWidgets.QAction('Rasterplot', self)
        self.add_rasterplot_tab.triggered.connect(self.open_rasterplot_settings_dialog)
        self.toolbar.addAction(self.add_rasterplot_tab)

        self.add_heatmap_tab = QtWidgets.QAction('Heatmap', self)
        self.add_rasterplot_tab.triggered.connect(self.open_heatmap_settings_dialog)
        self.toolbar.addAction(self.add_heatmap_tab)

        main_layout.addWidget(self.toolbar)

        sub_layout = QtWidgets.QHBoxLayout(self)
        sub_layout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        mea_grid_and_minor_widgets_layout = QtWidgets.QVBoxLayout(self)
        mea_grid_and_minor_widgets_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.file_manager = FileManager(self, self.reader.file_path)
        mea_grid_and_minor_widgets_layout.addWidget(self.file_manager)
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

        # make sure widget visibility matches tool bar button check states
        self.file_manager.setVisible(self.show_file_manager.isChecked())
        self.mea_grid.setVisible(self.show_mea_grid.isChecked())

    def open_heatmap_settings_dialog(self, is_pressed):
        allowed_modes = [PlotSettings.Mode.MCS]
        if self.file_manager.get_verified_meae_file() is not None:
            allowed_modes.append(PlotSettings.Mode.MEAE)
        if self.file_manager.get_verified_sc_file() is not None:
            allowed_modes.append(PlotSettings.Mode.SC)
        # To Do: change rasterplot settings to general plot settings
        settings_dialog = PlotSettingsDialog(self, allowed_modes, self.plot_settings)
        if settings_dialog.exec() == 1:  # 'Execute' clicked
            self.plot_settings = settings_dialog.get_settings()
            # overwrite global settings as well
            Settings.instance.plot_settings = self.plot_settings

            # initialise plotting
            if self.plot_settings.mode == PlotSettings.Mode.MCS:
                heatmap_tab = HeatmapTab(self, self.reader, self.plot_settings)
                self.tab_widget.addTab(heatmap_tab, "Heatmap")
            elif self.plot_settings.mode == PlotSettings.Mode.MEAE:
                meae_path = self.file_manager.get_verified_meae_file()
                meae_reader = MeaeDataReader(meae_path)
                heatmap_tab = HeatmapTab(self, meae_reader, self.plot_settings)
                self.tab_widget.addTab(heatmap_tab, "Heatmap")
            elif self.plot_settings.mode == PlotSettings.Mode.SC:
                sc_path = self.file_manager.get_verified_sc_file()
                sc_reader = SCDataReader(sc_path)
                heatmap_tab = HeatmapTab(self, sc_reader, self.plot_settings)
                self.tab_widget.addTab(heatmap_tab, "Heatmap")

    def open_rasterplot_settings_dialog(self, is_pressed):
        # determine allowed modes
        allowed_modes = [PlotSettings.Mode.MCS]
        if self.file_manager.get_verified_meae_file() is not None:
            allowed_modes.append(PlotSettings.Mode.MEAE)
        if self.file_manager.get_verified_sc_file() is not None:
            allowed_modes.append(PlotSettings.Mode.SC)

        settings_dialog = PlotSettingsDialog(self, allowed_modes, self.plot_settings)
        if settings_dialog.exec() == 1:  # 'Execute' clicked
            self.plot_settings = settings_dialog.get_settings()
            # overwrite global settings as well
            Settings.instance.raserplot_settings = self.plot_settings

            # initialise plotting
            if self.plot_settings.mode == PlotSettings.Mode.MCS:
                rasterplot_tab = RasterplotTab(self, self.reader, self.plot_settings)
                self.tab_widget.addTab(rasterplot_tab, "Rasterplot")
            elif self.plot_settings.mode == PlotSettings.Mode.MEAE:
                # self.reader.file.close() ?
                meae_path = self.file_manager.get_verified_meae_file()
                meae_reader = MeaeDataReader(meae_path)
                rasterplot_tab = RasterplotTab(self, meae_reader, self.plot_settings)
                self.tab_widget.addTab(rasterplot_tab, "Rasterplot")
            elif self.plot_settings.mode == PlotSettings.Mode.SC:
                sc_path = self.file_manager.get_verified_sc_file()
                sc_reader = SCDataReader(sc_path)
                rasterplot_tab = RasterplotTab(self, sc_reader, self.plot_settings)
                self.tab_widget.addTab(rasterplot_tab, "Rasterplot")

    def on_show_file_manager(self, is_pressed):
        self.file_manager.setVisible(is_pressed)

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
    def add_csd_plot_to_tabs(self):
        csd_plot_tab = CsdPlotTab(self, self.reader)
        self.tab_widget.addTab(csd_plot_tab, "CSD Plot")
        csd_plot_tab.plot()

    # @QtCore.pyqtSlot()
    # def open_plot_dialog(self):
    #     plot_dialog = PlotDialog(None, self.reader)
    #     plot_dialog.exec_()

