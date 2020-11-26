class SpikeDetectionSettings:

    class FileMode:
        MCS = 0
        MEAE = 1

    class Mode:
        PEAKS = 0
        TROUGHS = 1
        BOTH = 2

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    def __init__(self, initial_mode=FileMode.MCS):
        self.file_mode = initial_mode
        self.spike_window = 0.2  # in seconds
        self.mode = SpikeDetectionSettings.Mode.BOTH
        self.threshold_factor = 5
        self.save_spiketimes = False
        self.channel_selection = SpikeDetectionSettings.ChannelSelection.ALL

    def to_dict(self):
        result = dict()
        result["file_mode"] = self.file_mode
        result["spike_window"] = self.spike_window
        result["mode"] = self.mode
        result["threshold_factor"] = self.threshold_factor
        result["save spiketimes"] = self.save_spiketimes
        result["channel selection"] = self.channel_selection
        return result

    def from_dict(self, dictionary):
        if "file_mode" in dictionary.keys():
            self.file_mode = dictionary["file mode"]
        if "spike_window" in dictionary.keys():
            self.spike_window = dictionary["spike_window"]
        if "mode" in dictionary.keys():
            self.mode = dictionary["mode"]
        if "threshold_factor" in dictionary.keys():
            self.threshold_factor = dictionary["threshold_factor"]
        if "save spiketimes" in dictionary.keys():
            self.save_spiketimes = dictionary["save spiketimes"]
        if "channel selection" in dictionary.keys():
            self.channel_selection = dictionary["channel selection"]
