from PyQt5 import QtCore
import numpy as np


class FrequencyAnalysisThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, reader, grid_indices):
        super().__init__(parent)
        self.reader = reader
        self.labels = self.reader.labels
        self.grid_indices = grid_indices

        self.frequencies = None

    def analyzing_frequencies(self, reader):
        # idea behind this function is to go through MEA channels and compute the fast fourier transform to this channel
        # and afterwards, additionally the hann window is computed, so the FT is done on hann*signal to prevent leakage
        # effects
        frequencies = []
        ids = reader.channel_ids
        selected_ids = [ids[g_idx] for g_idx in self.grid_indices]
        for idx, ch_id in enumerate(selected_ids):
            label = self.labels[ch_id]
            scaled_signal = reader.get_scaled_channel(label)
            # call function to scale signal -> question is, if the effects will then be so soft as with the CSD video
            # spectrograms
            hann = np.hanning(len(scaled_signal))
            y_hann = np.fft.fft(hann*scaled_signal)
            frequencies.append(y_hann)
            progress = round(((idx + 1) / len(selected_ids)) * 100.0, 2)  # change idx of same_len_labels at the
            self.progress_made.emit(progress)
        return frequencies

    def run(self):
        self.operation_changed.emit('Analyzing frequency components of channels')
        self.frequencies = self.analyzing_frequencies(self.reader)
        self.finished.emit()
