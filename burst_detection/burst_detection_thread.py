from PyQt5 import QtCore
import numpy as np


class BurstDetectionThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, spiketimes, grid_labels, settings):
        super().__init__(parent)
        self.spiketimes = spiketimes
        self.grid_labels = grid_labels
        self.settings = settings

        self.all_bursts = None

    def work(self):
        # in order to determine which spikes belonged to bursts, we have to go through all the spike times of all
        # channels
        # skip channels that had less spikes than necessary
        self.all_bursts = []
        self.operation_changed.emit('Detecting bursts.')
        for idx, channel_spiketimes in enumerate(self.spiketimes):                                   # spike times are stored as indices
            channel_spiketimes = np.array(channel_spiketimes, dtype='int64')
            if len(channel_spiketimes) < self.settings.min_spikes_per_burst:
                continue
            # set up a set and a empty list to store spike indices contributing to bursts
            channel_burst_indices = set()
            current_burst_indices = []
            for current_spike_index in range(len(channel_spiketimes)):
                if len(current_burst_indices) == 0:
                    current_burst_indices.append(current_spike_index)
                else:   # at least one spike is in the list
                    first_spike_time_index = current_burst_indices[0]
                    first_spike_time = channel_spiketimes[first_spike_time_index]

                    current_spike_time = channel_spiketimes[current_spike_index]

                    if (current_spike_time - first_spike_time) <= self.settings.max_spike_time_diff:
                        # current spike is in the burst time window -> add to list and continue
                        for burst_index in current_burst_indices:
                            current_burst_indices.append(burst_index)
                    else:
                        # current spike is no longer in the time window of a burst
                        if len(current_burst_indices) >= self.settings.min_spikes_per_burst:
                            # at least three spikes -> burst
                            for burst_index in current_burst_indices:
                                channel_burst_indices.add(burst_index)
                        current_burst_indices = [current_spike_index]
                        current_burst_indices = [index for index in current_burst_indices
                                                 if (current_spike_time - channel_spiketimes[index])
                                                 <= self.settings.max_spike_time_diff]

            # end of inner for loop -> do not forget to add the last burst
            if len(current_burst_indices) >= self.settings.min_spikes_per_burst:
                for burst_spike_index in current_burst_indices:
                    channel_burst_indices.add(burst_spike_index)

            burst_spike_index_list = list(channel_burst_indices)
            burst_spike_index_list.sort()
            self.data_updated.emit([self.grid_labels[idx], burst_spike_index_list])
            self.all_bursts.append(burst_spike_index_list.copy())

            return self.all_bursts

    def run(self):
        self.all_bursts = self.work()
        self.finished.emit()




