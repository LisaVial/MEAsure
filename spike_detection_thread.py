from PyQt5 import QtCore
import numpy as np


class SpikeDetectionThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, reader):
        super().__init__(parent)
        self.reader = reader

        self.spike_mat = None
        self.spike_indices = None
        self.live_plotter = None

    def get_signal(self, electrode_stream, channel_id, chunk_size=10000):
        min_index = 0
        max_index = electrode_stream.channel_data.shape[1]
        length = (max_index - min_index)
        signal = np.empty(shape=(length,))  # create empty numpy ndarray with shape already set

        current_start_index = min_index

        while current_start_index < length:
            current_end_index = min(current_start_index + chunk_size - 1, max_index)
            result_pair = electrode_stream.get_channel_in_range(channel_id, current_start_index, current_end_index)
            chunk = result_pair[0]
            signal[current_start_index:(current_start_index + len(result_pair[0]))] = chunk
            time = electrode_stream.get_channel_sample_timestamps(channel_id, current_start_index,
                                                                  current_end_index)
            current_start_index = current_end_index + 1
        return signal

    def spike_detection(self, mea_data_reader):
        indices = []
        spike_mat = []

        reader = mea_data_reader
        signals = reader.voltage_traces
        ids = reader.channel_indices
        labels = reader.labels
        fs = reader.sampling_frequency

        above_upper_threshold = False
        below_lower_threshold = False
        current_extreme_index_and_value = None  # current local minimum or maximum

        for index, channel_id in enumerate(ids):
            signal = signals[channel_id]
            threshold = 4.5 * np.median(np.absolute(signal)) / 0.6745
            for idx, value in enumerate(signal):
                if above_upper_threshold:  # last value was above positive threshold limit
                    if value <= threshold:  # leaving upper area
                        # -> add current maximum index to list (unless its empty)
                        indices.append(current_extreme_index_and_value[0])
                    else:  # still above positive threshold
                        # check if value is bigger than current maximum
                        if value > current_extreme_index_and_value[1]:
                            current_extreme_index_and_value = (index, value)

                elif below_lower_threshold:  # last value was below negative threshold limit
                    if value <= threshold:  # leaving lower area
                        # -> add current minimum index to list (unless its empty)
                        indices.append(current_extreme_index_and_value[0])
                    else:  # still below negative threshold
                        # check if value is smaller than current maximum
                        if value < current_extreme_index_and_value[1]:
                            current_extreme_index_and_value = (index, value)

                else:  # last value was within threshold limits
                    if value > threshold or value < -threshold:  # crossing threshold limit
                        # initialise new local extreme value
                        current_extreme_index_and_value = (index, value)

                # update state
                below_lower_threshold = (value < -threshold)
                above_upper_threshold = (value > threshold)
            spiketimes = np.asarray(indices) * (1/fs)
            spike_mat.append(spiketimes)
            data = [list(signal[::312]), list(spiketimes), list(threshold)]
            self.data_updated.emit(data)
            progress = round(((idx + 1) / len(ids)) * 100.0, 2)
            self.progress_made.emit(progress)

        return indices, spike_mat

    def run(self):
        self.operation_changed.emit("Detecting spikes")
        self.spike_indices, self.spike_mat = self.spike_detection(self.reader)
        self.finished.emit()
