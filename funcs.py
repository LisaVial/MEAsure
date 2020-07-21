import numpy as np


def text_parser(file_path):
    with open(file_path) as file:
        lines = file.readlines()

        time = []
        voltage = []
        for line in lines:
            if '\t' in line and '[' not in line:
                line_ls = line.split('\t')
                time.append(float(line_ls[0]))
                sec_ele = line_ls[1].split('\n')
                voltage.append(float(sec_ele[0]))
    return time, voltage


def spike_detection(file):
    spike_mat = []
    electrode_stream = file.recordings[0].analog_streams[0]
    ids = [c.channel_id for c in electrode_stream.channel_infos.values()]
    for i in range(len(ids)):
        channel_id = ids[i]
        signal = electrode_stream.get_channel_in_range(channel_id, 0, electrode_stream.channel_data.shape[1])[0]
        channel_info = electrode_stream.channel_infos[channel_id]
        sampling_frequency = channel_info.sampling_frequency.magnitude
        noise_std = np.std(signal)
        noise_mad = np.median(np.absolute(signal)) / 0.6745
        spike_threshold = -5 * noise_mad
        fs = int(electrode_stream.channel_infos[channel_id].sampling_frequency.magnitude)
        crossings = detect_threshold_crossings(signal, fs, spike_threshold, 0.003)  # dead time of 3 ms
        spks = align_to_minimum(signal, fs, crossings, 0.002)  # search range 2 ms
        timestamps = spks / fs
        spike_mat.append(timestamps)
        print(((i+1)/len(ids))*100, ' % finished')
    return spike_mat


# from tutorial on github
def detect_threshold_crossings(signal, fs, threshold, dead_time):
    """
    Detect threshold crossings in a signal with dead time and return them as an array

    The signal transitions from a sample above the threshold to a sample below the threshold for a detection and
    the last detection has to be more than dead_time apart from the current one.

    :param signal: The signal as a 1-dimensional numpy array
    :param fs: The sampling frequency in Hz
    :param threshold: The threshold for the signal
    :param dead_time: The dead time in seconds.
    """
    dead_time_idx = dead_time * fs
    threshold_crossings = np.diff((signal <= threshold).astype(int) > 0).nonzero()[0]
    distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    while not np.all(distance_sufficient):
        # repeatedly remove all threshold crossings that violate the dead_time
        threshold_crossings = threshold_crossings[distance_sufficient]
        distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    return threshold_crossings


def get_next_minimum(signal, index, max_samples_to_search):
    """
    Returns the index of the next minimum in the signal after an index

    :param signal: The signal as a 1-dimensional numpy array
    :param index: The scalar index
    :param max_samples_to_search: The number of samples to search for a minimum after the index
    """
    search_end_idx = min(index + max_samples_to_search, signal.shape[0])
    min_idx = np.argmin(signal[index:search_end_idx])
    return index + min_idx


def align_to_minimum(signal, fs, threshold_crossings, search_range):
    """
    Returns the index of the next negative spike peak for all threshold crossings

    :param signal: The signal as a 1-dimensional numpy array
    :param fs: The sampling frequency in Hz
    :param threshold_crossings: The array of indices where the signal crossed the detection threshold
    :param search_range: The maximum duration in seconds to search for the minimum after each crossing
    """
    search_end = int(search_range * fs)
    aligned_spikes = [get_next_minimum(signal, t, search_end) for t in threshold_crossings]
    return np.array(aligned_spikes)