class RasterplotSettings:

    class Mode:
        MCS = 0
        MEAE = 1
        SC = 2

    def __init__(self, initial_mode=Mode.MCS):
        self.mode = initial_mode

    def to_dict(self):
        result = dict()
        result['mode'] = self.mode
        return result

    def from_dict(self, dictionary):
        if 'mode' in dictionary.keys():
            self.mode = dictionary['mode']
