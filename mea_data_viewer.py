import McsPy
import McsPy.McsData
from McsPy import ureg, Q_
import matplotlib.pyplot as plt
import os
from IPython import embed


class MeaDataViewer:
    def __init__(self, path, grid_label):
        file_path = path
        grid_label = grid_label
        file = McsPy.McsData.RawData(file_path)
        electrode_stream = file.recordings[0].analog_streams[0]
        labels = [c.label for c in electrode_stream.channel_infos.values()]
        channel_idx = [idx for idx, label in enumerate(labels) if label == grid_label]
        print(labels[0])
