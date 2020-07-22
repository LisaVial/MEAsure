from PyQt5 import QtCore, QtWidgets
import sys
import time

from plot_widget import PlotWidget
import funcs as f


class SpikeDetectionThread(QtCore.QThread):
    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent, n, file):
        super(SpikeDetectionThread, self).__init__(parent)
        self.n = n
        self.file = file
        self.plot_widget = PlotWidget

    def run(self):
        self.total.emit(self.n)
        i = 0
        spike_mat = f.spike_detection(self.file)
        self.plot_widget.start_plotting(spike_mat)
        while i < self.n:
            if time.time() % 1 == 0:
                i += 1
                self.update.emit()


class Progress(QtWidgets.QProgressBar):

    def __init__(self, parent=None):
        super(Progress, self).__init__(parent)
        self.setValue(0)

        self.thread = SpikeDetectionThread(self, 3)

        self.thread.total.connect(self.setMaximum)
        self.thread.update.connect(self.update)
        self.thread.finnished.connect(self.close)

        self.n = 0
        self.thread.start()

    def update(self):
        self.n += 1
        print(self.n)
        self.setValue(self.n)
