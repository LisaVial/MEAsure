from PyQt5 import QtCore
from scipy.signal import filtfilt, butter


class FilterThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, reader, filter_mode, cutoff_1, cutoff_2, grid_indices):
        super().__init__(parent)
        self.reader = reader

        self.filter_mode = filter_mode
        self.cut_1 = cutoff_1
        self.cut_2 = cutoff_2
        self.grid_indices = grid_indices

        self.filtered_mat = None

    def butter_bandpass(self, lowcut, highcut, fs, order=2):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=2):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    def butter_filter(self, cutoff, fs, mode, order=4):
        nyq = 0.5 * fs
        normal_cutoff = cutoff/nyq
        b, a = butter(order, normal_cutoff, btype=mode, analog=False)
        return b, a

    def butter_div_filters(self, data, cutoff_freq, fs, mode):
        # as far as I understood it, all three filter types (low, high, notch) can be applied with these functions
        # and which filter will be applied at the end depends on the chosen mode
        b, a = self.butter_filter(cutoff_freq, fs, mode)
        y = filtfilt(b, a, data)
        return y

    def filtering(self, mea_data_reader):
        filter_mat = []
        reader = mea_data_reader
        signals = reader.voltage_traces
        ids = reader.channel_indices
        labels = reader.labels
        fs = reader.sampling_frequency
        selected_ids = [ids[g_idx] for g_idx in self.grid_indices]
        for idx, ch_id in enumerate(selected_ids):
            # in this case, the whole channel should be loaded, since the filter should be applied at once
            signal = signals[ch_id]
            if self.filter_mode == 0:
                filtered = self.butter_div_filters(signal, self.cut_1, fs, 'low')
            elif self.filter_mode == 1:
                filtered = self.butter_div_filters(signal, self.cut_1, fs, 'high')
            elif self.filter_mode == 2:
                filtered = self.butter_bandpass_filter(signal, self.cut_1, self.cut_2, fs)
            filter_mat.append(filtered)

            data = [list(signal[::312]), list(filtered[::312]), str(labels[self.grid_indices[idx]])]
            self.data_updated.emit(data)

            progress = round(((idx + 1) / len(selected_ids)) * 100.0, 2)  # change idx of same_len_labels at the
            # end of testing
            self.progress_made.emit(progress)
        return filter_mat

    def run(self):
        # file = reader.open_mea_file(self.mea_file)
        self.operation_changed.emit('Filtering traces')
        self.filtered_mat = self.filtering(self.reader)
        self.finished.emit()
