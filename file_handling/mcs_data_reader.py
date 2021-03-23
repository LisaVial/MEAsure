import numpy as np
import h5py
import time

from utility.channel_utility import ChannelUtility


class McsDataReader:
    def __init__(self, path):
        self.file_path = path
        self.filename = path.split('/')[-1]
        t0 = time.time()
        self.file = self.open_mea_file()
        t1 = time.time() - t0
        print("Time elapsed for file opening: ", t1)
        try:
            self.voltage_traces, self.sampling_frequency, self.duration = self.get_data_of_file()
        except KeyError:
            self.voltage_traces = self.file['scaled']
            self.sampling_frequency = 10000.0
            self.duration = 300.0
        try:
            self.channel_ids, self.labels = self.get_channel_ids()
        except KeyError:
            self.channel_ids = range(252)
            channel_utility = ChannelUtility()
            self.labels = channel_utility.get_channel_labels()

    def get_channel_id(self, label):
        for ch in self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']:
            if label == ch[4].decode('utf8'):
                return ch[0]

    def get_scaled_channel(self, label):
        # so far unclear: will this be done once? -> might be difficult regarding memory
        # do this for each single channel while the channel is needed -> function has to be called each time when
        # signal is needed
        id = self.get_channel_id(label)
        vt = self.voltage_traces[id]
        conversion_factor = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['ConversionFactor']
        exponent = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['Exponent'] + 6
        # 6 = pV -> uV
        scaled_trace = vt * conversion_factor * np.power(10.0, exponent)
        return scaled_trace

    def open_mea_file(self):
        file = h5py.File(self.file_path, 'r')
        return file

    def get_data_of_file(self):
        voltage_traces = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelData'][:]
        sampling_frequency = 1000000 / \
                             self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']['Tick'][0]
        duration_index = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelDataTimeStamps'][0][2]
        duration = duration_index * (1 / sampling_frequency)
        # infos of the recording:
        # Total recording duration in microseconds:
        # file['Data']['Recording_0'].attrs['Duration']
        # Conversion factor for the mapping ADC-Step ⇒ measured value:
        # file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']['ConversionFactor']
        # Matrix ChannelDataTimeStamps → k × 3 matrix of segments where the rows are one segment and the columns are:
        # first column → time stamp of the first sample point of the segment
        # second column → first index (column) of the segment in ChannelData
        # third column → last index (column) of the segment in ChannelData
        # file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelDataTimeStamps'][0][2]
        # file = McsPy.McsData.RawData(path)
        return voltage_traces, sampling_frequency, duration

    def get_channel_ids(self):
        ids = [ch[0] for ch in self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]
        labels = [ch[4].decode('utf8') for ch in
                  self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]
        same_len_labels = [str(label[0]) + '0' + str(label[1]) if len(label) < 3 else label for label in labels]
        ordered_indices = list(np.argsort(same_len_labels))
        return list(np.asarray(ids)[ordered_indices]), list(np.asarray(labels)[ordered_indices])
