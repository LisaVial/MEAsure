import os
import numpy as np
import h5py


class MeaeDataReader:
    def __init__(self, path):
        self.filepath = path
        self.file = h5py.File(path, 'r')

        self.sampling_frequency = self.file['fs']
        self.channel_indices = self.file['channel_indices']
        self.channel_labels = self.file['channel_labels']

        filtered = "/filter" in self.file
        if filtered:
            self.filtered_traces = self.file['filter']


        has_spike_times = False
        for key in self.file.keys():
            if key.startswith("spiketimes_"):
                has_spike_times = True
                break

        if has_spike_times:
            self.spiketimes = self.retrieve_spiketimes()
            print(self.spiketimes)

    def retrieve_spiketimes(self):
        same_len_keys = []
        for key in list(self.file.keys()):
            if 'times' in key:
                if len(key) == 6:
                    current_key = key[:5] + '00' + key[-1:]
                    same_len_keys.append(current_key)
                elif len(key) == 7:
                    current_key = key[:5] + '0' + key[-1:]
                    same_len_keys.append(current_key)
                else:
                    same_len_keys.append(key)
        indices = np.argsort(same_len_keys)

        sorted_spiketimes = []
        for idx in indices:
            key = 'spiketimes_' + str(idx)
            if key in list(self.file.keys()):
                # ToDo: check how to retrieve sampling frequency from SC results file and then divide spiketimes by fs
                sorted_spiketimes.append(self.file[key][:])
        return sorted_spiketimes