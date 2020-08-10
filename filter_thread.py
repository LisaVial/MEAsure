from PyQt5 import QtCore
import numpy as np
from scipy.signal import lfilter, butter

from mea_data_reader import MeaDataReader


class FilterThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, plot_widget, mea_file, filter_mode, cutoff_1, cutoff_2):
        super().__init__(parent)
        self.mea_file = mea_file
        self.plot_widget = plot_widget
        self.filter_mode = filter_mode
        self.cut_1 = cutoff_1
        self.cut_2 = cutoff_2

        self.filtered_mat = None

    def butter_bandpass(self, lowcut, highcut, fs, order=2):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=2):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def butter_filter(self, cutoff, fs, mode, order=2):
        nyq = 0.5 * fs
        normal_cutoff = cutoff/nyq
        b, a = butter(order, normal_cutoff, btype=mode, analog=False)
        return b, a

    def butter_div_filters(self, data, cutoff_freq, fs, mode):
        # as far as I understood it, all three filter types (low, high, notch) can be applied with these functions
        # and which filter will be applied at the end depends on the chosen mode
        b, a = self.butter_filter(cutoff_freq, fs, mode)
        y = lfilter(b, a, data)
        return y

    def filtering(self, file):
        filter_mat = []
        electrode_stream = file.recordings[0].analog_streams[0]
        ids = [c.channel_id for c in electrode_stream.channel_infos.values()]
        # the next to lines ensure, that the for loop analyzes channels in the 'right order', but reversed
        labels = [electrode_stream.channel_infos[id].info['Label'] for id in ids]
        same_len_labels = [str(label[0]) + '0' + str(label[1]) if len(label) < 3 else label for label in labels]
        for idx, ch_id in enumerate(reversed(np.argsort(same_len_labels[:2]))):    # only first two channels for testing
            channel_id = ids[idx]
            # in this case, the whole channel should be loaded, since the filter should be applied at once
            signal = electrode_stream.get_channel_in_range(channel_id, 0, electrode_stream.channel_data.shape[1])[0]
            channel_label = ch_id
            fs = int(electrode_stream.channel_infos[channel_id].sampling_frequency.magnitude)
            if self.filter_mode == 0:
                filtered = self.butter_div_filters(signal, self.cut_1, fs, 'low')
            elif self.filter_mode == 1:
                filtered = self.butter_div_filters(signal, self.cut_1, fs, 'high')
            elif self.filter_mode == 2:
                filtered = self.butter_bandpass_filter(signal, self.cut_1, self.cut_2, fs)
            # elif self.filter_mode == 3:
            #     filtered = self.butter_bandpass_filter(signal, self.cut_1, self.cut_2, fs)

            # filter_mat.append(channel_label)
            filter_mat.append(filtered)

            progress = round(((idx + 1) / len(same_len_labels[:2])) * 100.0, 2)  # change idx of same_len_labels at the
            # end of testing
            self.progress_made.emit(progress)
        print(filter_mat)
        return filter_mat

    def run(self):
        reader = MeaDataReader()
        file = reader.open_mea_file(self.mea_file)
        self.operation_changed.emit('Filtering traces')
        self.filtered_mat = self.filtering(file)
        self.finished.emit()
