from PyQt5 import QtCore
import numpy as np
import funcs
import math
from IPython import embed

from mea_data_reader import MeaDataReader
from live_plot import LivePlotter


class SpikeDetectionThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, plot_widget, mea_file):
        super().__init__(parent)
        self.mea_file = mea_file
        self.plot_widget = plot_widget

        # self.x_vals = [0]
        # self.y_vals = [0]
        # self.data_line = self.plot_widget.plot(self.x_vals, self.y_vals, pen='#006E7D')
        #
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(50)
        # self.timer.start()

        self.spike_mat = None
        self.signal = None
        self.spike_threshold = None
        self.current_timestamps = None
        self.time = None
        # self.timer.timeout.connect(self.update_plot_data(self.time, self.signal))
        self.live_plotter = None

    # def update_plot_data(self, time, signal):
    #     while self.time is None or self.signal is None:
    #         continue
    #     self.x_vals.append(time)
    #     self.y_vals.append(signal)
    #     self.data_line.setData(self.x_vals, self.y_vals)

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

    def spike_detection(self, file):
        spike_mat = []
        electrode_stream = file.recordings[0].analog_streams[0]
        ids = [c.channel_id for c in electrode_stream.channel_infos.values()]
        for i in range(len(ids)): #range(len(ids)):
            channel_id = ids[i]
            #signal = electrode_stream.get_channel_in_range(channel_id, 0, electrode_stream.channel_data.shape[1])[0]
            self.signal = self.get_signal(electrode_stream, channel_id)
            channel_info = electrode_stream.channel_infos[channel_id]
            channel_label = channel_info.label
            noise_mad = np.median(np.absolute(self.signal)) / 0.6745
            self.spike_threshold = -5 * noise_mad
            fs = int(electrode_stream.channel_infos[channel_id].sampling_frequency.magnitude)
            # if i == 0:
            #     time = np.arange(duration) * (1 / fs)
            #     spike_mat.append(['time [s]', time])
            crossings = funcs.detect_threshold_crossings(self.signal, fs, self.spike_threshold, 0.003)
            # dead time of 3 ms
            spks = funcs.align_to_minimum(self.signal, fs, crossings, 0.002)  # search range 2 ms
            self.current_timestamps = spks / fs
            # self.live_plotter = LivePlotter(self.plot_widget.figure, self.signal, self.spike_threshold,
            #                                 self.current_timestamps)
            spike_mat.append(channel_label)
            spike_mat.append(self.current_timestamps)

            progress = round(((i + 1) / len(ids)) * 100.0, 2)
            self.progress_made.emit(progress)

            return spike_mat

    def run(self):
        reader = MeaDataReader()
        file = reader.open_mea_file(self.mea_file)
        self.operation_changed.emit("Detecting spikes")
        self.spike_mat = self.spike_detection(file)
        self.finished.emit()
