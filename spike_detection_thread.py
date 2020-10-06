from PyQt5 import QtCore
import numpy as np
from IPython import embed
from spike_detection.spike_detection_settings import SpikeDetectionSettings

class SpikeDetectionThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    single_spike_data_updated = QtCore.pyqtSignal(list)
    channel_data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, reader, spike_window, mode, threshold_factor):
        super().__init__(parent)
        self.reader = reader
        self.spike_window = spike_window
        self.mode = mode
        self.threshold_factor = threshold_factor
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
        fs = reader.sampling_frequency

        above_upper_threshold = False
        below_lower_threshold = False
        current_extreme_index_and_value = None  # current local minimum or maximum

        for idx, ch_id in enumerate(ids):
            # in this case, the whole channel should be loaded, since the filter should be applied at once
            signal = signals[ch_id]
            threshold = self.threshold_factor * np.median(np.absolute(signal) / 0.6745)
            collect_peaks = (self.mode == SpikeDetectionSettings.Mode.PEAKS or
                             self.mode == SpikeDetectionSettings.Mode.BOTH)
            collect_troughs = (self.mode == SpikeDetectionSettings.Mode.TROUGHS or
                               self.mode == SpikeDetectionSettings.Mode.BOTH)
            channel_spike_indices = []
            for index, value in enumerate(signal):
                if above_upper_threshold:  # last value was above positive threshold limit
                    if value <= threshold:  # leaving upper area
                        # -> add current maximum index to list
                        if collect_peaks:
                            channel_spike_indices.append(current_extreme_index_and_value[0])

                            lower_index = current_extreme_index_and_value[0] - int((self.spike_window/2) * fs)
                            upper_index = current_extreme_index_and_value[0] + int((self.spike_window/2) * fs)
                            single_spike_voltage = signal[lower_index:upper_index]
                            single_spike_index = (current_extreme_index_and_value[0] - lower_index)
                            single_spike_height = signal[current_extreme_index_and_value[0]]
                            single_spike_data = [single_spike_voltage, single_spike_index, single_spike_height,
                                                 threshold]
                            self.single_spike_data_updated.emit(single_spike_data)
                    else:  # still above positive threshold
                        # check if value is bigger than current maximum
                        if value > current_extreme_index_and_value[1]:
                            current_extreme_index_and_value = (index, value)

                elif below_lower_threshold:  # last value was below negative threshold limit
                    if value <= threshold:  # leaving lower area
                        # -> add current minimum index to list
                        if collect_troughs:
                            channel_spike_indices.append(current_extreme_index_and_value[0])

                            lower_index = current_extreme_index_and_value[0] - int((self.spike_window / 2) * fs)
                            upper_index = current_extreme_index_and_value[0] + int((self.spike_window / 2) * fs)
                            single_spike_voltage = signal[lower_index:upper_index]
                            single_spike_index = (current_extreme_index_and_value[0] - lower_index)
                            single_spike_height = signal[current_extreme_index_and_value[0]]
                            single_spike_data = [single_spike_voltage, single_spike_index, single_spike_height,
                                                 threshold]
                            self.single_spike_data_updated.emit(single_spike_data)
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
                indices.append(channel_spike_indices)
            progress = round(((idx + 1) / len(ids)) * 100.0, 2)
            self.progress_made.emit(progress)

            spiketimes = channel_spike_indices / fs
            spike_mat.append(spiketimes)
            data = [spiketimes]
            self.channel_data_updated.emit(data)
            # import matplotlib.pyplot as plt
            # plt.figure()
            # H,edges = np.histogram(signal, bins=1000)
            # centers = edges[:-1] + np.diff(edges)[0]/2
            # plt.plot(centers, H)
            # plt.show()

        return indices, spike_mat

    def run(self):
        self.operation_changed.emit("Detecting spikes")
        self.spike_indices, self.spike_mat = self.spike_detection(self.reader)
        self.finished.emit()
