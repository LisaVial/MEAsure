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

        # ToDo: check new saving strategy on one of Andrea's files later on
        spikes = "/spiketimes" in self.file
        if spikes:
            self.spiketimes = self.file['spiketimes']