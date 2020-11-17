from PyQt5 import QtCore


class FrequencyPlotCreationThread(QtCore.QThread):
    all_done_signal = QtCore.pyqtSignal()

    def __init__(self, plot_widget, tab, frequencies):
        super().__init__(plot_widget)
        self.plot_widget = plot_widget
        self.figure = self.plot_widget.figure
        self.frequency_analysis_tab = tab
        self.frequencies = frequencies

    def run(self):
        self.frequency_analysis_tab.plot(self.figure, self.frequencies)
        self.plot_widget.refresh_canvas()

        self.all_done_signal.emit()
