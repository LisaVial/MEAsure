class RasterplotSettings:

    class Mode:
        MEAE = 0
        SC = 1

    def __init__(self):
        self.mode = RasterplotSettings.Mode.SC

    def to_dict(self):
        result = dict()
        result['mode'] = self.mode
        return result

    def from_dict(self, dictionary):
        if 'mode' in dictionary.keys():
            self.mode = dictionary['mode']
