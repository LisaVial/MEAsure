import os
import numpy as np
import h5py
from IPython import embed


class SCDataReader:
    def __init__(self, path):
        self.filename = path.split('/')[-1]
        self.file = h5py.File(path, 'r')
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
            key = 'times_' + str(idx)
            if key in list(self.file.keys()):
                # ToDo: check how to retrieve sampling frequency from SC results file and then divide spiketimes by fs
                # -> in the spike check dialog this will be done by using the mcs file as well
                sorted_spiketimes.append(self.file[key][:])
        return sorted_spiketimes