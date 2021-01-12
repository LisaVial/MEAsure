import numpy as np
import h5py
import time


class McsDataReader:
    def __init__(self, path):
        self.file_path = path
        self.filename = path.split('/')[-1]
        t0 = time.time()
        self.file = self.open_mea_file()
        t1 = time.time() - t0
        print("Time elapsed for file opening: ", t1)
        self.voltage_traces, self.sampling_frequency, self.duration = self.get_data_of_file()
        self.channel_ids, self.labels = self.get_channel_ids()
        # t0 = time.time()
        # voltage_traces_test = self.read_voltage_traces_from_file()
        # t1 = time.time() - t0
        # print('time to load the whole recording of all electrodes:', t1)
        # self.current_file = dict()
        # self.current_file['sampling rate'] = self.sampling_frequency
        # self.current_file['duration'] = self.duration
        # self.current_file['channels'] = dict()
        # self.raw_voltage_traces = None
        # self.channel_ids, self.labels = self.get_channel_indices(self.file)
        # # embed()
        # for idx, label in enumerate(self.labels):
        #     self.current_file['channels'][str(label)] = dict()
        #     self.current_file['channels'][str(label)]['channel id'] = self.channel_ids[idx]
        #     self.current_file['channels'][str(label)]['raw trace'] = np.empty(int(self.duration *
        #                                                                           self.sampling_frequency))

    # def read_voltage_traces_from_file(self):
    #     return self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelData'][:]
    #
    # # for Danielas data the raw traces take almost 6 GB working memory, if stored in a dictionary. So, think of a way
    # # how to make further analysis feasible
    # # this function has to get back the respective trace of the dictionary, then, think about how to call it in the
    # # different scripts
    # def get_traces_with_label(self, label):
    #     return self.current_file['channels'][str(label)]['raw trace']
            
    # def assign_chunks(self, step_signal):
    #     # step signal will be an array with the dimension 252 x chunk_size
    #     for idx, channel_id in enumerate(self.channel_ids):
    #         self.current_file['channels'][str(self.labels[idx])]['raw trace'][int(step_signal[1]):int(step_signal[2])] \
    #             = step_signal[3][channel_id, :]

    def open_mea_file(self):
        file = h5py.File(self.file_path, 'r')
        return file

    def get_data_of_file(self):
        voltage_traces = self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelData'][:]
        print(voltage_traces)
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

    def get_channel_ids(self):
        ids = [ch[1] for ch in self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]
        labels = [ch[4].decode('utf8') for ch in
                  self.file['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel']]
        same_len_labels = [str(label[0]) + '0' + str(label[1]) if len(label) < 3 else label for label in labels]
        ordered_indices = list(np.argsort(same_len_labels))
        return list(np.asarray(ids)[ordered_indices]), list(np.asarray(labels)[ordered_indices])

