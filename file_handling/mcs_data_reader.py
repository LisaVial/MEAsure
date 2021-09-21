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

        # create list of labels (e.g. 'A3', 'G13', etc)
        # in the order they appear in the h5 file
        self._ordered_label_list = [ch[4].decode('ascii') for ch in
                                    self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]

        self.voltage_traces, self.sampling_frequency, self.duration = self.get_data_of_file()
        self.channel_ids, self.labels = self.get_channel_ids()

    def get_label_for_row_index(self, index: int):
        if index < 0 or index >= len(self._ordered_label_list):
            raise Exception('Invalid index "' + str(index) + '" given.')

        return self._ordered_label_list[index]

    def get_row_index_for_label(self, label: str):
        if len(label) < 2:
            raise Exception('Invalid label "' + label + '" given.')

        # make sure the first letter is upper case
        corrected_label = label[0].upper() + label[1:]

        # remove zero padding
        if corrected_label[1] == '0':
            corrected_label = corrected_label[0] + corrected_label[2:]

        index = self._ordered_label_list.index(corrected_label)
        if index < 0:
            raise Exception('Could not find label "' + label + '"')

        return index


    def get_channel_id(self, label):
        for ch in self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']:
            if label == ch[4].decode('utf8'):
                return ch[1]

    def get_scaled_channel(self, label):
        # so far unclear: will this be done once? -> might be difficult regarding memory
        # do this for each single channel while the channel is needed -> function has to be called each time when
        # signal is needed
        id_by_label = self.get_channel_id(label)
        vt = self.voltage_traces[id_by_label]
        conversion_factor = \
            self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'][0]['ConversionFactor']
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
        ids = [ch[1] for ch in self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]
        labels = [ch[4].decode('utf8') for ch in
                  self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]
        same_len_labels = [str(label[0]) + '0' + str(label[1]) if len(label) < 3 else label for label in labels]
        ordered_indices = list(np.argsort(same_len_labels))
        return list(np.asarray(ids)[ordered_indices]), list(np.asarray(labels)[ordered_indices])
