import os
import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from data_list_view import DataListView
from mea_grid import MeaGrid
from mea_data_viewer import MeaDataViewer


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
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

        self.rasterButton = QtWidgets.QPushButton(self.centralwidget)
        self.rasterButton.setText("Raster Plot")

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setAlignment(QtCore.Qt.AlignBottom)
        self.buttonLayout.addWidget(self.rasterButton)

        self.rasterButton.clicked.connect(self.initialize_raster_plot)

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

    @QtCore.pyqtSlot()
    def initialize_raster_plot(self):
        pass

    # the following lines create an exception hook
    # which allows to output Python exceptions while PyQt is running
    # taken from: https://stackoverflow.com/a/43039363/8928024
    sys._excepthook = sys.excepthook

    def my_exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = my_exception_hook
    # end of exception hook creation


application = QtWidgets.QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()

application.setActiveWindow(mainWindow)
sys.exit(application.exec())
