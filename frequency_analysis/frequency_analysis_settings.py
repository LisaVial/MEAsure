class FrequencyAnalysisSettings:

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    def __init__(self):
        self.channel_selection = FrequencyAnalysisSettings.ChannelSelection.ALL
        self.channel_time_selection = dict()

    def to_dict(self):
        result = dict()
        result['channel selection'] = self.channel_selection
        return result

    def from_dict(self, dictionary):
        if 'channel selection' in dictionary.keys():
            self.channel_selection = dictionary['channel selection']
