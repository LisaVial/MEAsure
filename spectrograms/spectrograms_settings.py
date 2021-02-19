class SpectrogramsSettings:

    class ChannelSelection:
        ALL = 0
        SELECTION = 1

    def __init__(self):
        self.channel_selection = SpectrogramsSettings.ChannelSelection.ALL

    def to_dict(self):
        result = dict()
        result['channel selection'] = self.channel_selection

    def from_dict(self, dict):
        if 'channel selection' in dict.keys():
            self.channel_selection = dict['channel selection']
