import os
import sys
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from IPython import embed
from data_list_view import DataListView
from funcs import text_parser
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.file_list_view = DataListView(self)

        self.data_file_list_dock_widget = QtWidgets.QDockWidget(self)
        self.data_file_list_dock_widget.setWidget(self.file_list_view)
        self.file_list_view.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)

        self.data_file_list_dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.data_file_list_dock_widget.setWindowTitle("Folder selection")
        self.data_file_list_dock_widget.setObjectName("folder-selection")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.data_file_list_dock_widget)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)
        self.addToolBar(NavigationToolbar(self.canvas, self))

        self.canvas.axes.plot([0, 0], [0, 0], '-')
        ax = self.canvas.axes
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

    @QtCore.pyqtSlot()
    def on_close_button_pressed(self):
        self.accept()

    def closeEvent(self, close_event):
        super().closeEvent(close_event)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def on_file_double_clicked(self, item):
        absolute_path = os.path.join(self.file_list_view.current_folder, item.text())
        self.update_plot(absolute_path)

    @QtCore.pyqtSlot()
    def update_plot(self, absolute_path):
        time, voltage = text_parser(absolute_path)
        self.canvas.axes.cla()
        self.canvas.axes.plot(time, voltage)
        self.canvas.axes.set_xlabel('time [s]')
        self.canvas.axes.set_ylabel('voltage ['+r'$\mu$'+'V]')
        ax = self.canvas.axes
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        self.canvas.draw()

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
