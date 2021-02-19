class FrequencyBandsAnalysisSettings:

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    class AnalysisMode:
        ICTAL = 0
        CSD = 1

    def __init__(self):
        self.channel_selection = FrequencyBandsAnalysisSettings.ChannelSelection.ALL
        self.analysis_mode = FrequencyBandsAnalysisSettings.AnalysisMode.ICTAL

    def to_dict(self):
        result = dict()
        result['channel selection'] = self.channel_selection
        result['analysis mode'] = self.analysis_mode

    def from_dict(self, dictionary):
        if 'channel selection' in dictionary.keys():
            self.channel_selection = dictionary['channel selection']
        if 'analysis mode' in dictionary.keys():
            self.analysis_mode = dictionary['analysis mode']
