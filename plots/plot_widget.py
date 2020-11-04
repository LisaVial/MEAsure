import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class PlotWidget(QtWidgets.QWidget):
    def __init__(self, parent, plot_name):
        super().__init__(parent)
        self.plot_name = plot_name
        self.plot_thread = None

        self.figure = Figure()
        self.figure.subplots_adjust(left=0.1, right=0.9,
                                    bottom=0.1, top=0.9,
                                    hspace=0.3, wspace=0.3)
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)
        # self.graph_widget = pg.PlotWidget()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

    def clear_figure(self):
        self.figure.clear()

    def refresh_canvas(self):
        self.canvas.draw()

    def closeEvent(self, close_event):
        super().closeEvent(close_event)