from PyQt5 import QtCore
import numpy as np
from scipy.signal import savgol_filter, hilbert, find_peaks


class HilbertTransformThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progreass_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, reader, grid_labels):
        super().__init__(parent)
        self.reader = reader
        self.grid_labels = grid_labels
        self.filtered = None
        self.hilbert_transforms = None
        self.peaks = None

    def work(self):
        self.operation_changed.emit('filtering with savitzky golay filter')
        self.filtered = []
        self.hilbert_transforms = []
        self.peaks = []
        for label in self.grid_labels:
            vt = self.reader.get_scaled_channel(label)
            filtered_channel = savgol_filter(vt, 1001, 4)   # 1001 represents window length and 4 polynomial order
            self.filtered.append(filtered_channel)
            self.operation_changed.emit('calculating hilbert transform')
            analytic_signal = hilbert(filtered_channel)
            amplitudes = np.abs(analytic_signal)
            self.hilbert_transforms.append(amplitudes)
            # ToDo: get the threshold into the settings
            threshold = 6 * np.median(np.absolute(filtered_channel) / 0.6745)
            peaks = find_peaks(amplitudes, height=threshold)
            self.peaks.append(peaks)
            peak_diff = np.diff(peaks)
            epilepsy_peaks = np.where(peak_diff <= 125000)



