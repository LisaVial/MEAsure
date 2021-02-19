from PyQt5 import QtCore
import scipy.signal as signal


class SpectrogramsThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, reader, grid_indices, grid_labels, filtered):
        super().__init__(parent)
        self.reader = reader
        self.grid_indices = grid_indices
        self.grid_labels = grid_labels
        self.filtered = filtered

        self.frequencies, self.time, self.Sxx = None, None, None

    def calculating_spectrogram(self, reader):
        frequencies = []
        time = []
        Sxx = []
        # analysis of raw traces:
        # ids = reader.channel_ids
        # selected_ids = [ids[g_idx] for g_idx in self.grid_indices]
        # for idx, ch_id in enumerate(selected_ids):
        #   label = reader.labels[ch_id]
        for idx in range(len(self.filtered)):
            label = self.grid_labels[idx]
            filtered_trace = self.filtered[idx]
            sampling_rate = reader.sampling_frequency
            freqs, t, S_xx = signal.spectrogram(filtered_trace, sampling_rate, nperseg=2**10, noverlap=2**8)
            frequencies.append(freqs)
            time.append(t)
            Sxx.append(S_xx)
            progress = round((idx + 1) / len(self.filtered) * 100.0, 2)
            self.progress_made.emit(progress)
        return frequencies, time, Sxx

    def run(self):
        self.operation_changed.emit('Calculation spectrograms...')
        self.frequencies, self.time, self.Sxx = self.calculating_spectrogram(self.reader)
        self.finished.emit()
