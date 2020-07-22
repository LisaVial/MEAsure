import os
import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from data_list_view import DataListView
from mea_grid import MeaGrid
from settings import Settings, load_settings_from_file


class MainWindow(QtWidgets.QMainWindow):
    settings_file_name = "local-settings.json"

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)

        self.file_list_view = DataListView(self)
        self.centralwidget = QtWidgets.QWidget(self)

        self.data_file_list_dock_widget = QtWidgets.QDockWidget(self)
        self.data_file_list_dock_widget.setWidget(self.file_list_view)

        self.file_list_view.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.data_file_list_dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.data_file_list_dock_widget.setWindowTitle("Folder selection")
        self.data_file_list_dock_widget.setObjectName("folder-selection")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.data_file_list_dock_widget)

        self.load_settings()

    def load_settings(self):
        settings = None
        if os.path.isfile(MainWindow.settings_file_name):
            with open(MainWindow.settings_file_name) as settings_file:
                settings = load_settings_from_file(settings_file)

        if settings:
            self.file_list_view.set_current_folder(settings.last_folder)
            self.restoreGeometry(QtCore.QByteArray.fromBase64(settings.main_window_geometry))
            self.restoreState(QtCore.QByteArray.fromBase64(settings.main_window_state))


    @QtCore.pyqtSlot()
    def on_close_button_pressed(self):
        self.accept()

    def closeEvent(self, close_event):
        self.save_settings()
        super().closeEvent(close_event)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def on_file_double_clicked(self, item):
        absolute_path = os.path.join(self.file_list_view.current_folder, item.text())
        mea_grid = MeaGrid(self)
        self.setCentralWidget(mea_grid)

    def save_settings(self):
        settings = Settings()
        settings.last_folder = self.file_list_view.current_folder
        settings.main_window_geometry = self.saveGeometry().toBase64()
        settings.main_window_state = self.saveState().toBase64()
        try:
            with open(MainWindow.settings_file_name, 'w') as settings_file:
                settings.save(settings_file)
        except OSError:
            pass


