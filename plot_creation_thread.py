import PyQt5.QtCore as QtCore


class PlotCreationThread(QtCore.QThread):
    all_done_signal = QtCore.pyqtSignal()

    def __init__(self, plot_widget, figure):
        super().__init__(plot_widget)
        self.plot_widget = plot_widget
        self.figure = figure

    def run(self):
        self.main_window.plot(self.figure)
        self.plot_widget.refresh_canvas()

        self.all_done_signal.emit()