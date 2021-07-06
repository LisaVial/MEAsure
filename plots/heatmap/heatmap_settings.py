class HeatmapSettings:

    class Mode:
        MCS = 0
        MEAE = 1
        SC = 2

    def __init__(self, initial_mode=Mode.SC):
        self.mode = initial_mode
        self.heatmap_for_normalizing = None

    def to_dict(self):
        result = dict()
        result['mode'] = self.mode
        return result

    def from_dict(self, dictionary):
        if 'mode' in dictionary.keys():
            self.mode = dictionary['mode']