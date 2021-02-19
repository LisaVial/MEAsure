import csv


# sub classes for specific results
class FrequencyAnalysisResult:
    # todo: bring distinction of different analysis in here, for now it'll be hard coded
    # band_names = 'delta', 'theta', 'alpha', 'smr', 'beta', 'gamma'
    band_names = '50 Hz', '350 Hz', 'alpha', 'smr', 'beta', 'gamma'

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


