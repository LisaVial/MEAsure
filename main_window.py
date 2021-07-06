import os

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

from data_list_view import DataListView
from plot_list_view import PlotListView

from file_handling.mcs_data_reader import McsDataReader
from mea_file_tab_widget import MeaFileTabWidget

from plot_manager import PlotManager
from settings import Settings


# This script initializes the MainWindow of the MEAsure application. So the dialog the user sees once he or she starts
# the GUI via the start_gui.py script.
class MainWindow(QtWidgets.QMainWindow):
    settings_file_name = "local-settings.json"

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)

        app_icon = QtGui.QIcon("icon.png")
        self.setWindowIcon(app_icon)

        self.file_list_view = DataListView(self)

        # MainWindow has a different layout style than other widgets...
        # (https://doc.qt.io/qtforpython/_images/mainwindowlayout.png)

        self.data_file_list_dock_widget = QtWidgets.QDockWidget(self)
        self.data_file_list_dock_widget.setWidget(self.file_list_view)

        self.file_list_view.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.data_file_list_dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.data_file_list_dock_widget.setWindowTitle("Folder selection")
        self.data_file_list_dock_widget.setObjectName("folder-selection")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.data_file_list_dock_widget)
        
        self.plot_list_view = PlotListView(self)

        self.plot_list_dock_widget = QtWidgets.QDockWidget(self)
        self.plot_list_dock_widget.setWidget(self.plot_list_view)
        self.plot_list_dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.plot_list_dock_widget.setWindowTitle('Save Plots')
        self.plot_list_dock_widget.setObjectName('plot-saver')
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.plot_list_dock_widget)

        self.mea_tab_widget = MeaFileTabWidget(self)
        # ...basically you set a centralwidget which will be the focus point of the window
        self.setCentralWidget(self.mea_tab_widget)

        self.load_settings()

        self.toolbar = QtWidgets.QToolBar(self)
        self.show_file_selection = QtWidgets.QAction("File selection", self)
        file_selection_icon = QtGui.QIcon("./icons/file_selection_icon.png")
        self.show_file_selection.setIcon(file_selection_icon)
        self.show_file_selection.triggered.connect(self.on_show_file_selection)
        self.show_file_selection.setCheckable(True)  # kann an/aus sein
        self.show_file_selection.setChecked(False)
        self.toolbar.addAction(self.show_file_selection)
        # self.show_file_selection.setChecked(False)
        self.show_plot_manager = QtWidgets.QAction("Save Plots", self)
        plot_manager_icon = QtGui.QIcon("./icons/plot_manager_icon.png")
        self.show_plot_manager.setIcon(plot_manager_icon)
        self.show_plot_manager.setCheckable(True)
        self.show_plot_manager.setChecked(False)
        self.show_plot_manager.triggered.connect(self.on_show_plot_manager)
        self.toolbar.addAction(self.show_plot_manager)
        self.open_multiple_files_analysis_dialog = QtWidgets.QAction("analyse multiple files")
        multiple_file_analysis_icon = QtGui.QIcon("./icons/multiple_files_icon.png")
        self.open_multiple_files_analysis_dialog.setIcon(multiple_file_analysis_icon)
        self.open_multiple_files_analysis_dialog.connect(self.open_mfa_dialog)
        self.toolbar.addAction(self.open_multiple_files_analysis_dialog)
        self.addToolBar(self.toolbar)

        plot_manager = PlotManager()
        plot_manager.set_plot_list_view(self.plot_list_view)

    def load_settings(self):
        settings = Settings()
        if os.path.isfile(MainWindow.settings_file_name):
            with open(MainWindow.settings_file_name) as settings_file:
                settings.load_settings_from_file(settings_file)

        if settings:
            self.file_list_view.set_current_folder(settings.last_folder)
            self.restoreGeometry(QtCore.QByteArray.fromBase64(settings.main_window_geometry))
            self.restoreState(QtCore.QByteArray.fromBase64(settings.main_window_state))

    @QtCore.pyqtSlot()
    def on_close_button_pressed(self):
        self.accept()

    def open_mfa_dialog(self, is_pressed):
        

    def on_show_plot_manager(self, is_pressed):
        self.plot_list_dock_widget.setVisible(is_pressed)

    def on_show_file_selection(self, is_pressed):
        self.data_file_list_dock_widget.setVisible(is_pressed)

    def closeEvent(self, close_event):
        self.save_settings()
        super().closeEvent(close_event)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def on_file_double_clicked(self, item):
        absolute_path = os.path.join(self.file_list_view.current_folder, item.text())
        self.mea_tab_widget.show_mea_file_view(absolute_path)

    def save_settings(self):
        settings = Settings.instance
        settings.last_folder = self.file_list_view.current_folder
        settings.main_window_geometry = self.saveGeometry().toBase64()
        settings.main_window_state = self.saveState().toBase64()
        try:
            with open(MainWindow.settings_file_name, 'w') as settings_file:
                settings.save(settings_file)
        except OSError:
            pass

    def get_heatmaps(self):
        heatmap_tabs = []
        for widget_index in range(self.mea_tab_widget.count()):
            mea_file_view = self.mea_tab_widget.widget(widget_index)
            if mea_file_view and mea_file_view.heatmap_tab:
                heatmap_tabs.append(mea_file_view.heatmap_tab)
        return heatmap_tabs
