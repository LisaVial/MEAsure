from PyQt5 import QtCore
import numpy as np


class BurstDetectionThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, parent, spiketimes, grid_labels, grid_indices, sampling_rate, settings):
        super().__init__(parent)
        self.spiketimes = spiketimes
        self.grid_labels = grid_labels
        self.grid_indices = grid_indices
        self.fs = sampling_rate
        self.settings = settings

        self.all_bursts = None

    def work(self):
        self.all_bursts = []
        self.operation_changed.emit('Detecting bursts.')
        # first, we iterate through spiketime_indices of different channels
        for idx, channel_spiketimes in enumerate(self.spiketimes):      # spike times are stored as indices
            mcs_index = self.grid_indices[idx]
            # just store the spiketime_indices of current channel in a different dtyppe
            channel_spiketimes = np.array(channel_spiketimes, dtype='int64')
            # we skip the channels that have too less spiketimes for a burst
            if len(channel_spiketimes) < self.settings.min_spikes_per_burst:
                continue
            # set up a set to store verfied burst-spike times indices
            channel_burst_indices = set()
            # set up a list to store candidates for burst-spike time indices
            current_burst_indices = []
            # then, we iterate through the spike time indices of the current channel
            # current spike index ranges from (0 - len(channel spiketime indices))
            for current_spike_index in range(len(channel_spiketimes)):
                # if there are no spike time indices stored yet, we are going to store the first one that comes across
                if len(current_burst_indices) == 0:
                    # first, map back to the whole voltage trace as reference for indices
                    current_spike_time = channel_spiketimes[current_spike_index]
                    # and then actually save this spike time index
                    current_burst_indices.append(current_spike_time)
                else:   # at least one spike is in the list
                    # as reference spike time index we consider the first spike of the current burst indices list
                    first_spike_time = current_burst_indices[0]
                    # we are going to compare the reference spike time index with the one we currently are looking at
                    current_spike_time = channel_spiketimes[current_spike_index]
                    # now we check, if the time difference between these spike time indices meets the condition to be
                    # a burst
                    if (current_spike_time - first_spike_time) <= self.settings.max_spike_time_diff * self.fs:
                        # current spike is in the burst time window -> add each to list and continue
                        for burst_index in current_burst_indices:
                            channel_burst_indices.add(burst_index)
                    else:       # current spike is no longer in the time window of a burst
                        # we check if there have been enough spike time indices contributing to a burst so that it
                        # actually is a burst
                        if len(current_burst_indices) >= self.settings.min_spikes_per_burst:
                            # add all the found burst indices to the final channel burst indices set
                            # (I used a set here, because it won't have duplicate entries)
                            for burst_index in current_burst_indices:
                                channel_burst_indices.add(burst_index)
                        # iterate once more through the found burst spike time indices to keep the spike time indices
                        # that were close enough to conrtribute to the burst
                        current_burst_indices = [index for index in current_burst_indices
                                                 if (current_spike_time - index)
                                                 <= self.settings.max_spike_time_diff]
                        # the current spike time index has also to be added to the list
                        current_burst_indices = [current_spike_time]

                # end of inner for loop -> do not forget to add the last burst
                if len(current_burst_indices) >= self.settings.min_spikes_per_burst:
                    for burst_spike_index in current_burst_indices:
                        channel_burst_indices.add(burst_spike_index)

                burst_spike_index_list = list(channel_burst_indices)
                burst_spike_index_list.sort()
                self.all_bursts.append(burst_spike_index_list.copy())

                self.data_updated.emit([self.grid_labels[idx], mcs_index, burst_spike_index_list])

                progress = round((idx + 1) / len(self.grid_labels) * 100.0, 2)
                self.progress_made.emit(progress)

        return self.all_bursts

    def run(self):
        self.all_bursts = self.work()
        self.finished.emit()




