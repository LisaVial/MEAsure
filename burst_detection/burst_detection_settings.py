class BurstDetectionSettings:

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    def __init__(self):
        self.channel_selection = BurstDetectionSettings.ChannelSelection.ALL
        self.max_spike_time_diff = 0.1      #s
        self.min_spikes_per_burst = 3

    def to_dict(self):
        result = dict()
        result['channel selection'] = self.channel_selection

    def from_dict(self, dictionary):
        if 'channel selection' in dictionary.keys():
            self.channel_selection = dictionary['channel selection']
