from PyQt5 import QtCore
import numpy as np
from scipy.signal import savgol_filter, hilbert


def split_index_list(index_list, min_distance):
    # note: index_list must be sorted

    if len(index_list) == 0:
        return []

    result = []
    last_index = index_list[0]
    current_sub_list = [last_index]

    for current_index in index_list[1:]:

        if (current_index - last_index) >= min_distance:
            # append current sub list (without current index) to result
            result.append(current_sub_list.copy())
            # create a new sub list
            current_sub_list.clear()

        current_sub_list.append(current_index)
        last_index = current_index

    # do not forget to add last sub list to result as well
    if len(current_sub_list) > 0:
        result.append(current_sub_list.copy())

    return result


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

        self.epileptic_indices = dict()

    def work(self):
        # since our binning is 1s, the indices actually also represent the time
        for idx, label in enumerate(self.grid_labels):
            self.epileptic_indices[label] = []
            vt = self.reader.get_scaled_channel(label)
            self.operation_changed.emit('filtering with savitzky golay filter')
            filtered_channel = savgol_filter(vt, 1001, 4)   # 1001 represents window length and 4 polynomial order
            self.operation_changed.emit('calculating hilbert transform')
            analytic_signal = hilbert(filtered_channel)
            amplitudes = np.abs(analytic_signal)

            # take the median without the first two seconds, which probably include the puffing artefact
            puffing_indices = int(self.reader.sampling_frequency * 3.5)
            threshold = self.threshold_factor * np.median(np.absolute(filtered_channel[puffing_indices:])) / 0.6745

            binned_time = np.linspace(0, int(np.ceil(self.duration)), int(np.ceil(self.duration)))
            binned_values = [np.mean(amplitudes[int(i * self.fs):int((i + 1) * self.fs)]) for i in binned_time[:-1]]

            self.operation_changed.emit('Searching for epileptic areas in the signal')
            channel_epileptic_indices = []
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
                    channel_epileptic_indices += ([bin_idx] + neighbours)

            # remove duplicate indices from list
            epileptic_index_set = set()
            for epileptic_index in channel_epileptic_indices:
                epileptic_index_set.add(epileptic_index)
            channel_epileptic_indices = list(epileptic_index_set)
            channel_epileptic_indices.sort()

            min_distance = 6  # indices
            self.epileptic_indices[label] = split_index_list(channel_epileptic_indices, min_distance)

            data = [binned_time, binned_values, threshold, channel_epileptic_indices]
            progress = round(((idx + 1) / len(self.grid_labels)) * 100.0, 2)
            self.progress_made.emit(progress)
            self.data_updated.emit(data)
            if len(channel_epileptic_indices) < self.min_peaks_per_seizure:
                continue
        return

    def run(self):
        self.operation_changed.emit('Initializing Hilbert Transform')
        self.epileptic_indices.clear()
        self.work()
        self.finished.emit()



