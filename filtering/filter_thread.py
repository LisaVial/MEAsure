from PyQt5 import QtCore
from scipy.signal import filtfilt, butter
import time


# In this script the QThread which handles filtering in the background is set up
class FilterThread(QtCore.QThread):
    # Line 8 - 11 defines different signals which will be sent to the FilterTab in the course of running this thread
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    # As always, the FilterThread class has to be initialized
    def __init__(self, parent, reader, filter_mode, cutoff_1, cutoff_2, grid_indices, grid_labels):
        super().__init__(parent)
        self.reader = reader

        self.filter_mode = filter_mode
        self.cut_1 = cutoff_1
        self.cut_2 = cutoff_2
        self.grid_indices = grid_indices
        self.grid_labels = grid_labels

        self.filtered_mat = None

    # Line 26 - 49 set up different filtering functions
    def butter_bandpass(self, lowcut, highcut, fs, order=2):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=2):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    def butter_filter(self, cutoff, fs, mode, order=4):
        nyq = 0.5 * fs
        normal_cutoff = cutoff/nyq
        b, a = butter(order, normal_cutoff, btype=mode, analog=False)
        return b, a

    def butter_div_filters(self, data, cutoff_freq, fs, mode):
        # todo: check if this still works
        # as far as I understood it, all three filter types (low, high, notch) can be applied with these functions
        # and which filter will be applied at the end depends on the chosen mode
        b, a = self.butter_filter(cutoff_freq, fs, mode)
        y = filtfilt(b, a, data)
        return y

    def filtering(self, mea_data_reader):
        """
        This function filters the selected channels with the according filter
        :param mea_data_reader: McsDataReader to get the signals of the channels
        :return: filter_mat and signals for the live plot, progress bar and label
        """
        # Set up filter_mat to store filtered traces in and get all necessary variables
        filter_mat = []
        reader = mea_data_reader
        signals = reader.voltage_traces
        ids = reader.channel_ids
        labels = reader.labels
        fs = reader.sampling_frequency
        # With this one liner (list comprehension) only selected channel ids are selected according to chosen
        # grid_indices
        # selected_ids = [ids[g_idx] for g_idx in self.grid_indices]

        for idx, label in enumerate(self.grid_labels):
            # Right now, all the channels should be loaded and filtered, since the way storing of .meae files is set
            # up it will get very confusing fast.
            # So basically grid_indices should be a list with the length of all channel indices
            t1 = time.time()
            scaled_signal = reader.get_scaled_channel(label)
            t2 = time.time() - t1
            print('Time to load channel data: ', t2)
            t3 = time.time()
            # Here the filter is chosen according to the filter mode
            if self.filter_mode == 0:
                filtered = self.butter_div_filters(scaled_signal, self.cut_1, fs, 'low')
            elif self.filter_mode == 1:
                filtered = self.butter_div_filters(scaled_signal, self.cut_1, fs, 'high')
            elif self.filter_mode == 2:
                filtered = self.butter_bandpass_filter(scaled_signal, self.cut_1, self.cut_2, fs)
            # Once data is filtered, it is appended to the filter_mat list.
            filter_mat.append(filtered)
            t4 = time.time() - t3
            print('Time to filter data:', t4)
            # Here the list of the currently created filtered trace is created. Only every 312th data point of the
            # original signal is sent, to be able to plot the signals, since there are for once not enough pixels on
            # screen to plot all data points correctly and also, for massive data loads also the pyqtgraph plot widget
            # starts lagging.
            data = [list(scaled_signal[::312]), list(filtered[::312]), str(labels[self.grid_indices[idx]])]
            self.data_updated.emit(data)    # Here, the signal is sent to the FilterTav

            # Here, the progress signal is calculated and then sent to the FilterTab
            progress = round(((idx + 1) / len(self.grid_labels)) * 100.0, 2)
            self.progress_made.emit(progress)
        return filter_mat

    def run(self):
        # This function calls the filtering function and by doing so starts the actual filtering
        self.operation_changed.emit('Filtering traces')
        self.filtered_mat = self.filtering(self.reader)
        # Once all selected channels are filtered, a finished signal is sent to the FilterTab.
        self.finished.emit()
