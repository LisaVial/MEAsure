class FilterSettings:

    class Mode:
        LOWPASS = 0
        HIGHPASS = 1
        BANDPASS = 2
        NOTCH = 3

    def __init__(self):
        self.lower_cutoff = 100
        self.upper_cutoff = 3000
        self.mode = FilterSettings.Mode.BANDPASS
        self.save_filtered_traces = False

    def to_dict(self):
        result = dict()
        result["mode"] = self.mode
        result["lower cutoff"] = self.lower_cutoff
        result["upper cutoff"] = self.upper_cutoff
        result["save filtered traces"] = self.save_filtered_traces
        return result

    def from_dict(self, dictionary):
        if "mode" in dictionary.keys():
            self.mode = dictionary["mode"]
        if "lower cutoff" in dictionary.keys():
            self.lower_cutoff = dictionary["lower cutoff"]
        if "upper cutoff" in dictionary.keys():
            self.upper_cutoff = dictionary["Upper cutoff"]
        if "save filtered traces" in dictionary.keys():
            self.save_filtered_traces = dictionary["save filtered traces"]