from PyQt5 import QtCore
import numpy as np
from scipy.signal import savgol_filter, hilbert


class HilbertTransformThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, reader, grid_labels, threshold_factor,
                 min_peaks_per_seizure):
        super().__init__(parent)
        self.reader = reader
        self.duration = self.reader.duration
        self.fs = self.reader.sampling_frequency
        self.grid_labels = grid_labels
        self.threshold_factor = threshold_factor
        self.min_peaks_per_seizure = min_peaks_per_seizure

        self.epileptic_indices = None

    def work(self):
        self.epileptic_indices = []     # since our binning is 1s, the indices actually also represent the time
        for idx, label in enumerate(self.grid_labels):
            vt = self.reader.get_scaled_channel(label)
            self.operation_changed.emit('filtering with savitzky golay filter')
            filtered_channel = savgol_filter(vt, 1001, 4)   # 1001 represents window length and 4 polynomial order
            self.operation_changed.emit('calculating hilbert transform')
            analytic_signal = hilbert(filtered_channel)
            amplitudes = np.abs(analytic_signal)

            threshold = self.threshold_factor * np.median(np.absolute(filtered_channel) / 0.6745)

            binned_time = np.linspace(0, int(np.ceil(self.duration)), int(np.ceil(self.duration)))
            binned_values = [np.mean(amplitudes[int(i * self.fs):int((i + 1) * self.fs)]) for i in binned_time[:-1]]

            self.operation_changed.emit('Searching for epileptic areas in the signal')
            self.epileptic_indices = []
            # start at the 6th value (because of puffing artefact) and go through the values in bins of ten
            for bin_idx in range(6, len(binned_time[:-6])):
                # print('bin index:', bin_idx)
                middle_bin = binned_values[bin_idx]
                if middle_bin < threshold:
                    continue  # skip middle bins below threshold
                neighbours = []
                for ci in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
                    # print('comparison index:', ci)
                    if binned_values[bin_idx + ci] >= threshold:
                        neighbours.append(bin_idx + ci)
                if len(neighbours) >= 3:
                    self.epileptic_indices += list([bin_idx] + neighbours)
            epileptic_peak_indices = set()
            for epileptic_index in self.epileptic_indices:
                epileptic_peak_indices.add(epileptic_index)
            epileptic_indices_list = list(epileptic_peak_indices)
            epileptic_indices_list.sort()
            data = [binned_time, binned_values, threshold, epileptic_indices_list]
            progress = round(((idx + 1) / len(self.grid_labels)) * 100.0, 2)
            self.progress_made.emit(progress)
            self.data_updated.emit(data)
            if len(epileptic_indices_list) < self.min_peaks_per_seizure:
                continue
        return self.epileptic_indices

    def run(self):
        self.operation_changed.emit('Initializing Hilbert Transform')
        self.epileptic_indices = self.work()
        self.finished.emit()



