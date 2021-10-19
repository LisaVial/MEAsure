import csv
from frequency_bands_analysis.frequency_bands_analysis_settings import FrequencyBandsAnalysisSettings


# sub classes for specific results
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

    def set_filter_mat(self, filter_mat):
        self._filter_mat = filter_mat
        print(self._filter_mat)

    def set_frequency_mat(self, frequency_mat):
        self._frequency_mat = frequency_mat
        print(self._frequency_mat)

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
        sorted(self.frequency_analysis_results, key=lambda result: result.label)

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # write header
            writer.writerow(FrequencyAnalysisResult.get_header())

            for frequency_result in self.frequency_analysis_results:
                writer.writerow(frequency_result.get_as_row())


