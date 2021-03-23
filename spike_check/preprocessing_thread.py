from PyQt5 import QtCore
import numpy as np
from scipy.signal import filtfilt, butter
import time
from utility.channel_utility import ChannelUtility


class PreprocessingThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, mcs_reader, sc_reader):
        super().__init__(parent)
        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader

        self.chunk_size = 30    # [s] -> info from spyking circus log

        self.scaled_matrix = None
        self.filtered_matrix = None
        self.preproc_matrix = None

        self.labels = self.mcs_reader.labels

    def get_scaled_channel_matrix(self, labels):
        self.operation_changed.emit('Scaling traces...')
        scaled_matrix = []
        for idx, label in enumerate(labels):
            scaled_channels_voltage_trace = self.mcs_reader.get_scaled_channel(label)
            scaled_matrix.append(scaled_channels_voltage_trace)
            progress = round(((idx + 1) / len(labels)) * 100.0, 2)
            self.progress_made.emit(progress)
        return scaled_matrix

    def butter_bandpass(self, lowcut, highcut, fs, order=3):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='pass')
        return b, a

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=3):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = filtfilt(b, a, data, axis=0)
        return y

    def preprocess_file(self):
        self.operation_changed.emit('Filtering traces and substracting median...')
        num_of_elements = len(self.scaled_matrix[0])
        dead_channels = [0, 1, 14, 15, 16, 30, 31, 46, 47, 62, 63, 78, 79, 94, 95, 110, 111, 126, 127, 142, 143, 158,
                         159, 174, 175, 190, 191, 206, 207, 222, 223, 224, 238, 239, 240]

        cluster_to_channel_index = dict()
        channel_to_cluster_index = dict()  # note: dead channels do not have a cluster

        cluster_index = 0
        for channel_index in range(ChannelUtility.get_label_count()):
            if channel_index not in dead_channels:
                cluster_to_channel_index[cluster_index] = channel_index
                channel_to_cluster_index[channel_index] = cluster_index
                cluster_index += 1  # increase cluster index

        fs = self.mcs_reader.sampling_frequency
        preproc_matrix = np.full([len(self.scaled_matrix), num_of_elements], np.nan)
        filtered_matrix = np.full([len(self.scaled_matrix), num_of_elements], np.nan)
        step_size = self.chunk_size * fs
        chunk_windows = np.arange(0, num_of_elements + step_size, step_size)
        spatial_matrix = self.sc_reader.retrieve_spatial_mat()
        # How many steps does it take, according to len of single channels, when we consider 30s chunks?:
        for i, chunk_idx in enumerate(chunk_windows[:-1]):
            local_chunk = np.asarray(self.scaled_matrix)[:, int(chunk_idx):int(chunk_windows[i+1])]
            filtered = self.butter_bandpass_filter(local_chunk, 300, 4750, fs)
            filtered_matrix[:, int(chunk_idx):int(chunk_windows[i+1])] = filtered
            filtered -= np.median(filtered, 0)
            global_median = np.median(filtered, 1)
            filtered -= global_median[:, np.newaxis]

            # ToDo: find a way to remove dead channels and add them together later
            # if self.label_index not in dead_channels:
            # filtered = np.dot(spatial_matrix, filtered)
            preproc_matrix[:, int(chunk_idx):int(chunk_windows[i+1])] = filtered
            progress = round(((i + 1) / len(chunk_windows[:-1])) * 100.0, 2)
            self.progress_made.emit(progress)
        return filtered_matrix, preproc_matrix

    def run(self):
        self.operation_changed.emit("preprocessing data")
        t0 = time.time()

        self.scaled_matrix = self.mcs_reader.voltage_traces
        self.filtered_matrix, self.preproc_matrix = self.preprocess_file()
        t1 = time.time() - t0
        print('time for preprocessing file: ', t1)
        self.finished.emit()
