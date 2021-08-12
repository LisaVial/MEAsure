from PyQt5 import QtCore
import scipy.signal as signal


class FrequencyBandAnalysisThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()
    data_updated = QtCore.pyqtSignal(list)

    def __init__(self, parent, reader, grid_indices, grid_labels, filtered):
        super().__init__(parent)
        self.reader = reader
        self.grid_indices = grid_indices
        self.grid_labels = grid_labels
        self.filtered = filtered
        self.frequencies, self.power = None, None

    def analyzing_frequency_bands(self):
        frequencies = []
        powers = []
        # if analysis is done without filtering before:
        # ids = reader.channel_ids
        # selected_ids = [ids[g_idx] for g_idx in self.grid_indices]
        # for idx, ch_id in enumerate(selected_ids):
        #     label = reader.labels[ch_id]
        for idx in range(len(self.grid_indices)):
            label = self.grid_labels[idx]
            # scaled_signal = reader.get_scaled_channel(label)
            filtered_trace = self.filtered[idx]
            # freqs, Pxx = signal.welch(scaled_signal, self.reader.sampling_frequency, nperseg=2**14)
            freqs, Pxx = signal.welch(filtered_trace, self.reader.sampling_frequency, nperseg=2**14)
            frequencies.append(freqs)
            powers.append(Pxx)
            data = [label, freqs, Pxx]
            self.data_updated.emit(data)
            progress = round(((idx + 1) / len(self.filtered)) * 100.0, 2)
            self.progress_made.emit(progress)
        return frequencies, powers

    def run(self):
        self.operation_changed.emit('Calculating Power Spectral Density of channels')
        self.frequencies, self.power = self.analyzing_frequency_bands()
        self.finished.emit()