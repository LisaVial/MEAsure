class HilbertTransformSettings:

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    def __init__(self):
        self.channel_selection = HilbertTransformSettings.ChannelSelection.ALL
        self.threshold_factor = 2
        self.min_peaks_per_seizure = 4

    def to_dict(self):
        result = dict()
        result['channel selection'] = self.channel_selection
        result['threshold factor'] = self.threshold_factor
        result['min peaks per seizure'] = self.min_peaks_per_seizure

    def from_dict(self, dictionary):
        if 'channel selection' in dictionary.keys():
            self.channel_selection = dictionary['channel selection']
        if 'threshold factor' in dictionary.keys():
            self.threshold_factor = dictionary['threshold factor']
        if 'min peaks per seizure' in dictionary.keys():
            self.min_peaks_per_seizure = dictionary['min peaks per seizure']