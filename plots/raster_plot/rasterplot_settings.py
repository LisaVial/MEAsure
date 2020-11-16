class RasterplotSettings:

    class Mode:
        MCS = 0
        MEAE = 1
        SC = 2

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    def __init__(self, initial_mode=Mode.MCS):
        self.mode = initial_mode
        self.channel_selection = RasterplotSettings.ChannelSelection.ALL

    def to_dict(self):
        result = dict()
        result['mode'] = self.mode
        result["channel selection"] = self.channel_selection
        return result

    def from_dict(self, dictionary):
        if 'mode' in dictionary.keys():
            self.mode = dictionary['mode']
        if "channel selection" in dictionary.keys():
            self.channel_selection = dictionary["channel selection"]