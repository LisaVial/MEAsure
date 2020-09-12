class SpikeDetectionSettings:

    class Mode:
        PEAKS = 0
        TROUGHS = 1
        BOTH = 2

    def __init__(self):
        self.spike_window = 0.2  # in seconds
        self.mode = SpikeDetectionSettings.Mode.BOTH
        self.threshold_factor = 5

    def to_dict(self):
        result = dict()
        result["spike_window"] = self.spike_window
        result["mode"] = self.mode
        result["threshold_factor"] = self.threshold_factor
        return result

    def from_dict(self, dictionary):
        if "spike_window" in dictionary.keys():
            self.spike_window = dictionary["spike_window"]
        if "mode" in dictionary.keys():
            self.mode = dictionary["mode"]
        if "threshold_factor" in dictionary.keys():
            self.threshold_factor = dictionary["threshold_factor"]