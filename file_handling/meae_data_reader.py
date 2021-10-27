import os
import numpy as np
import h5py


# This class was used to handle .meae files (which are also hdf5 files). These files were created when you filtered and
# saved the filtered trace to a new hdf5 file. This method could be extended to save all kind of result, but for now it
# is not directly needed.
class MeaeDataReader:
    def __init__(self, path):
        self.file_path = path
        self.filename = path.split('/')[-1]
        self.file = h5py.File(path, 'r')
        if 'fs' in list(self.file.keys()):
            self.sampling_frequency = self.file['fs'][()]
        if 'channel_labels' in list(self.file.keys()):
            self.channel_labels = self.file['channel_labels']

        filtered = "/filter" in self.file
        if filtered:
            self.filtered_traces = self.file['filter']
            self.channel_ids = range(len(self.filtered_traces))

        has_spike_times = False
        for key in self.file.keys():
            if key.startswith("spiketimes_"):
                has_spike_times = True
                break

        if has_spike_times:
            self.spiketimes = self.retrieve_spiketimes()

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
