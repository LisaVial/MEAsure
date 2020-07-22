import os
import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from data_list_view import DataListView
from mea_grid import MeaGrid
from mea_data_viewer import MeaDataViewer


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.file_list_view = DataListView(self)
        self.centralwidget = QtWidgets.QWidget(self)

        self.data_file_list_dock_widget = QtWidgets.QDockWidget(self)
        self.data_file_list_dock_widget.setWidget(self.file_list_view)

        self.file_list_view.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.data_file_list_dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.data_file_list_dock_widget.setWindowTitle("Folder selection")
        self.data_file_list_dock_widget.setObjectName("folder-selection")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.data_file_list_dock_widget)


    @QtCore.pyqtSlot()
    def on_close_button_pressed(self):
        self.accept()

    def closeEvent(self, close_event):
        super().closeEvent(close_event)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def on_file_double_clicked(self, item):
        absolute_path = os.path.join(self.file_list_view.current_folder, item.text())
        data_viewer = MeaDataViewer(absolute_path)
        self.mea_grid = MeaGrid(self)
        self.setCentralWidget(self.mea_grid)



