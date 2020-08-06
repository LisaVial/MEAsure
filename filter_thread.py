from PyQt5 import QtCore
import numpy as np
import funcs
from scipy.signal import lfilter

from mea_data_reader import MeaDataReader


class FilterThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, plot_widget, mea_file):
        super().__init__(parent)
        self.mea_file = mea_file
        self.plot_widget = plot_widget

        self.filtered_mat = None




    def butter_bandpass(self, lowcut, highcut, fs, order=2):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = self.butter(order, [low, high], btype='band')
        return b, a

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=2):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def filtering(self, file):
        filter_mat = []
        electrode_stream = file.recordings[0].analog_streams[0]
        ids = [c.channel_id for c in electrode_stream.channel_infos.values()]
        # the next to lines ensure, that the for loop analyzes channels in the 'right order', but reversed
        labels = [electrode_stream.channel_infos[id].info['Label'] for id in ids]
        same_len_labels = [str(label[0]) + '0' + str(label[1]) if len(label) < 3 else label for label in labels]
        for idx, ch_id in enumerate(reversed(np.argsort(same_len_labels))): #range(len(ids)):
            channel_id = ids[idx]
            # in this case, the whole channel should be loaded, since the filter should be applied at once
            signal = electrode_stream.get_channel_in_range(channel_id, 0, electrode_stream.channel_data.shape[1])[0]
            channel_label = ch_id
