import os
import numpy as np
import h5py
import time


class McsDataReader:
    def __init__(self, path):
        self.file_path = path
        self.filename = path.split('/')[-1]
        t0 = time.time()
        self.file = self.open_mea_file(path)
        t1 = time.time() - t0
        print("Time elapsed for file opening: ", t1)
        t2 = time.time()
        self.voltage_traces, self.sampling_frequency, self.duration = self.get_data_of_file()
        print(self.voltage_traces)
        print(self.voltage_traces.shape)
        t3 = time.time() - t2
        print("Time elapsed for opening vts (old): ", t3)
        self.channel_indices, self.labels = self.get_channel_indices(self.file)

    def open_mea_file(self, path):
        file = h5py.File(path, 'r')
        return file

    def get_data_of_file(self):
        voltage_traces = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelData'][()]
        sampling_frequency = 1000000/self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']['Tick'][0]
        duration_index = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelDataTimeStamps'][0][2]
        duration = duration_index * (1/sampling_frequency)
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

    def get_channel_indices(self, file):
        ids = [ch[1] for ch in self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]
        labels = [ch[4].decode('utf8') for ch in
                  self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]
        same_len_labels = [str(label[0]) + '0' + str(label[1]) if len(label) < 3 else label for label in labels]
        ordered_indices = list(np.argsort(same_len_labels))
        return list(np.asarray(ids)[ordered_indices]), list(np.asarray(labels)[ordered_indices])

    def get_signal(self, chunk_size=1000):
        min_index = 0
        max_index = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelData'][self.channel_indices[0]].shape[0]
        length = (max_index - min_index)
        signal = np.empty(shape=(length,))  # create empty numpy ndarray with shape already set

        current_start_index = min_index

        while current_start_index < length:
            current_end_index = min(current_start_index + chunk_size - 1, max_index)
            for i in range(max_index):
                chunk = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelData'][self.channel_indices[i]][current_start_index:current_end_index]
                signal[current_start_index:(current_start_index + len(chunk))] = chunk
                current_start_index = current_end_index + 1

        return signal

