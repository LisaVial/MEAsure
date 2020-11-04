import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from plots.plot_creation_thread import PlotCreationThread
from plot_manager import PlotManager


class PlotWidget(QtWidgets.QWidget):
    def __init__(self, parent, plot_name):
        super().__init__(parent)
        self.plot_name = plot_name
        self.plot_manager = PlotManager.instance

        self.plot_thread = None

        self.figure = Figure()
        self.figure.subplots_adjust(left=0.1, right=0.9,
                                    bottom=0.1, top=0.9,
                                    hspace=0.3, wspace=0.3)

        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

    def start_plotting(self):
        self.toolbar.hide()
        self.plot_thread = PlotCreationThread(self, self.figure)
        self.plot_thread.finished.connect(self.on_plot_thread_is_done)

        debug_mode = False  # set to 'True' in order to debug plot creation with embed
        if debug_mode:
            # synchronous plotting (runs in main thread and thus allows debugging)
            self.plot_thread.run()
        else:
            # asynchronous plotting (default):
            self.plot_thread.start()  # start will start thread (and run), but main thread will continue immediately

    def is_busy_plotting(self):
        return self.plot_thread is not None

    @QtCore.pyqtSlot()
    def on_plot_thread_is_done(self):
        self.plot_thread = None
        self.toolbar.show()
        self.plot_manager.add_plot(self)

    def clear_figure(self):
        self.figure.clear()

    def refresh_canvas(self):
        self.canvas.draw()

    def closeEvent(self, close_event):
        self.plot_manager.remove_plot(self)
        super().closeEvent(close_event)
