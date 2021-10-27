# This class handles the settings for filtering. The same structure is used for all methods implemented in MEAsure.
class FilterSettings:
    """
    The FilterSettings object is used to store chosen user settings for filtering
    """

    class Mode:
        """
        The Mode object classifies which filter type should be used
        """
        LOWPASS = 0
        HIGHPASS = 1
        BANDPASS = 2
        NOTCH = 3

    class ChannelSelection:
        """
        The ChannelSelection object classifies, if all channels of the MEA will be analyzed or only a few of them
        """
        ALL = 0
        SELECTION = 1

    def __init__(self):
        """
        initially the filter settings are set to a bandpass filter with cutoffs of 100 and 4750 Hz and all channels will
        be analyzed
        """
        self.lower_cutoff = 100
        self.upper_cutoff = 4750
        self.mode = FilterSettings.Mode.BANDPASS
        self.save_filtered_traces = False
        self.channel_selection = FilterSettings.ChannelSelection.ALL

    def to_dict(self):
        """
        This function is needed to save the user settings
        :return: dictionary of stored user settings
        """
        result = dict()
        result["mode"] = self.mode
        result["lower cutoff"] = self.lower_cutoff
        result["upper cutoff"] = self.upper_cutoff
        result["save filtered traces"] = self.save_filtered_traces
        result["channel selection"] = self.channel_selection
        return result

    def from_dict(self, dictionary):
        """
        This function is needed to load the user settings
        :return: variables of the FilterSettings object which were changed by the user
        """
        if "mode" in dictionary.keys():
            self.mode = dictionary["mode"]
        if "lower cutoff" in dictionary.keys():
            self.lower_cutoff = dictionary["lower cutoff"]
        if "upper cutoff" in dictionary.keys():
            self.upper_cutoff = dictionary["Upper cutoff"]
        if "save filtered traces" in dictionary.keys():
            self.save_filtered_traces = dictionary["save filtered traces"]
        if "channel selection" in dictionary.keys():
            self.channel_selection = dictionary["channel selection"]