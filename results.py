import csv
from frequency_bands_analysis.frequency_bands_analysis_settings import FrequencyBandsAnalysisSettings


# sub classes for specific results
class HilbertTransformData:
    def __init__(self, label, start_time, end_time):
        self.label = label
        self.start_time = start_time
        self.end_time = end_time
        self.duration = self.end_time - self.start_time

    @staticmethod
    def get_header():
        return ['label', 'start time', 'end time', 'duration']

    def get_as_row(self):
        row = [self.label, self.start_time, self.end_time, self.duration]
        return row


class SpikeCountData:
    def __init__(self, label, spikecounts):
        if len(label) == 3:
            self.label = label
        else:
            self.label = label[0] + '0' + label[1:]
        self.spike_counts = spikecounts

    @staticmethod
    def get_header():
        return ['label', 'spike counts']

    def get_as_row(self):
        row = [self.label, self.spike_counts]
        return row


class SpikeTimesData:
    def __init__(self, label, spiketimes):
        self.label = label
        self.spiketimes = spiketimes

    @staticmethod
    def get_header():
        return ['label', 'spiketimes']

    def get_as_row(self):
        row = [self.label, self.spiketimes]
        return row


class FrequencyAnalysisResult:
    settings = FrequencyBandsAnalysisSettings()
    if settings.analysis_mode == 0:
        band_names = 'delta', 'theta', 'alpha', 'beta', 'gamma'
    elif settings.analysis_mode == 1:
        band_names = '50 Hz', '350 Hz'

    # static method is called with FrequencyAnalysisResult.get_header
    # it does not need any 'self' data
    @staticmethod
    def get_header():
        return ['label'] + list(FrequencyAnalysisResult.band_names)

    def __init__(self, label, band_map):
        self.label = label
        self.band_map = band_map

    def get_as_row(self):
        row = [self.label]
        for band in FrequencyAnalysisResult.band_names:
            row.append(self.band_map[band])
        return row


class ResultStoring:
    def __init__(self):
        self._filter_mat = None
        self.spike_times = None
        self._frequency_mat = None

        # frequency analysis
        self.frequency_analysis_results = []

        # spiketimes
        self.spiketimes_data = []

        # spike counts
        self.spikecount_data = []

        # hilbert transform result
        self.hilbert_transforms = None

    def set_filter_mat(self, filter_mat):
        self._filter_mat = filter_mat

    def set_frequency_mat(self, frequency_mat):
        self._frequency_mat = frequency_mat

    def get_filter_mat(self):
        return self._filter_mat

    def get_frequency_mat(self):
        return self._frequency_mat

    def clear_frequency_analysis_results(self):
        self.frequency_analysis_results.clear()

    def add_frequency_analysis_result(self, label, band_map):
        self.frequency_analysis_results.append(FrequencyAnalysisResult(label, band_map))

    def save_frequency_analysis_results_to(self, file_path):
        # sort list of results by label
        self.frequency_analysis_results = sorted(self.frequency_analysis_results, key=lambda result: result.label)

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # write header
            writer.writerow(FrequencyAnalysisResult.get_header())

            for frequency_result in self.frequency_analysis_results:
                writer.writerow(frequency_result.get_as_row())

    def get_spiketimes_from_rasterplot(self, label, spiketimes):
        self.spiketimes_data.append(SpikeTimesData(label, spiketimes))

    def clear_spiketimes(self):
        self.spiketimes_data.clear()

    def save_rasterplot_data_to(self, file_path):
        self.spiketimes_data = sorted(self.spiketimes_data, key=lambda result: result.label)
        with open(file_path, 'w', newline='') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(SpikeTimesData.get_header())
            for spiketime_data in self.spiketimes_data:
                w.writerow(spiketime_data.get_as_row())

    def get_spike_counts_from_heatmap(self, label, spikecounts):
        self.spikecount_data.append(SpikeCountData(label, spikecounts))

    def clear_spikecounts(self):
        self.spikecount_data.clear()

    def save_spikecount_data_to(self, file_path):
        self.spikecount_data = sorted(self.spikecount_data, key=lambda result: result.label)
        with open(file_path, 'w', newline='') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(SpikeCountData.get_header())
            for spikecount_data in self.spikecount_data:
                w.writerow(spikecount_data.get_as_row())

    def set_hilbert_transform_data(self, epileptic_indices_dict):
        if self.hilbert_transforms is None:
            self.hilbert_transforms = []

        for key in epileptic_indices_dict.keys():
            for epileptic_indices_list in epileptic_indices_dict[key]:
                label = key
                start_time = min(epileptic_indices_list)
                end_time = max(epileptic_indices_list)
                self.hilbert_transforms.append(HilbertTransformData(label, start_time, end_time))

    def clear_hilbert_transform_data(self):
        self.hilbert_transforms.clear()

    def save_hilbert_transform_data_to(self, file_path):
        sorted_hilbert_transforms = sorted(self.hilbert_transforms, key=lambda result: result.label)
        with open(file_path, 'w', newline='') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(HilbertTransformData.get_header())
            for hilbert_transform_data in sorted_hilbert_transforms:
                w.writerow(hilbert_transform_data.get_as_row())
