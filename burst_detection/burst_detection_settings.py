class BurstDetectionSettings:

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    def __init__(self):
        self.channel_selection = BurstDetectionSettings.ChannelSelection.ALL
        self.max_spike_time_diff = 0.1      #s
        self.min_spikes_per_burst = 3