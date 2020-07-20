import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from plot_creation_thread import PlotCreationThread


class PlotWidget(QtWidgets.QWidget):
    def __init__(self, parent, grid_id):
        super().__init__(parent)

        self.plot_thread = None

        self.grid_id = grid_id

        self.figure = Figure()

        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.loading_label = QtWidgets.QLabel("    Plotting ...")
        self.loading_label.setFixedHeight(64)
        self.loading_label.hide()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.loading_label)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

    def start_plotting(self):
        self.loading_label.show()
        self.toolbar.hide()
        self.plot_thread = PlotCreationThread(self, self.figure)
        self.plot_thread.all_done_signal.connect(self.on_plot_thread_is_done)

        debug_mode = False
        if debug_mode:
            self.plot_thread.run()
        else:
            self.plot_thread.start()

    def is_busy_plotting(self):
        return self.plot_thread is not None

    @QtCore.pyqtSlot()
    def on_plot_thread_is_done(self):
        self.plot_thread = None
        self.loading_label.hide()
        self.toolbar.show()
        self.plot_manager.add_plot(self)

    def clear_figure(self):
        self.figure.clear()

    def refresh_canvas(self):
        self.canvas.draw()

    def closeEvent(self, close_event):
        self.plot_manager.remove_plot(self)
        super().closeEvent(close_event)