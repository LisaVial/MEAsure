from PyQt5 import QtCore
import numpy as np
import funcs


from mea_data_reader import MeaDataReader


class SpikeDetectionThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, plot_widget, mea_file):
        super().__init__(parent)
        self.mea_file = mea_file
        self.plot_widget = plot_widget
        self.spike_mat = None

    def spike_detection(self, file):
        spike_mat = []
        electrode_stream = file.recordings[0].analog_streams[0]
        duration = file.recordings[0].duration
        ids = [c.channel_id for c in electrode_stream.channel_infos.values()]
        for i in range(len(ids)): #range(len(ids)):
            channel_id = ids[i]
            signal = electrode_stream.get_channel_in_range(channel_id, 0, electrode_stream.channel_data.shape[1])[0]
            channel_info = electrode_stream.channel_infos[channel_id]
            channel_label = channel_info.label
            noise_mad = np.median(np.absolute(signal)) / 0.6745
            spike_threshold = -5 * noise_mad
            fs = int(electrode_stream.channel_infos[channel_id].sampling_frequency.magnitude)
            # if i == 0:
            #     time = np.arange(duration) * (1 / fs)
            #     spike_mat.append(['time [s]', time])
            crossings = funcs.detect_threshold_crossings(signal, fs, spike_threshold, 0.003)  # dead time of 3 ms
            spks = funcs.align_to_minimum(signal, fs, crossings, 0.002)  # search range 2 ms
            timestamps = spks / fs
            spike_mat.append(channel_label)
            spike_mat.append(timestamps)

            progress = round(((i + 1) / len(ids)) * 100.0, 2)
            self.progress_made.emit(progress)

        return spike_mat

    def run(self):
        reader = MeaDataReader()
        file = reader.open_mea_file(self.mea_file)
        self.operation_changed.emit("Detecting spikes")
        self.spike_mat = self.spike_detection(file)
        self.finished.emit()
