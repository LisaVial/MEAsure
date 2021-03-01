class RawTraceSettings:

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    def __init__(self):
        self.channel_selection = RawTraceSettings.ChannelSelection.ALL
        self.start_time = 0
        self.end_time = 1

    def to_dict(self):
        result = dict()
        result['channel selection'] = self.channel_selection
        result['start time'] = self.start_time
        result['end time'] = self.end_time
        return result

    def from_dict(self, dictionary):
        if 'channel selection' in dictionary.keys():
            self.channel_selection = dictionary['channel selection']
        if 'start time' in dictionary.keys():
            self.start_time = dictionary['start time']
        if 'end time' in dictionary.keys():
            self.end_time = dictionary['end time']
