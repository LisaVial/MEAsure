import os
import numpy as np
import h5py


class MeaeDataReader:
    def __init__(self, path):
        self.filepath = path
        self.file = h5py.File(path, 'r')

        self.sampling_frequency = self.file['fs']
        self.channel_indices = self.file['channel_indices']
        self.channel_labels = self.file['channel labels']

        filtered = "/filter" in self.file
        if filtered:
            self.filtered_traces = self.file['filter']

        # ToDo: normally, spiketimes should be saved in several datasets as the single arrays do not have the same len
        # ToDo: also change this in the spike detection dialog since the h5-saving-technique seems to be lost
        spikes = "/spiketimes_" in self.file
        if spikes:
            self.spiketimes = self.file['spiketimes']