import McsPy
import McsPy.McsData
from McsPy import ureg, Q_
import matplotlib.pyplot as plt
import os
from IPython import embed
import funcs as f


class MeaDataViewer:
    def __init__(self, path):
        file_path = path
        # grid_label = grid_label
        file = McsPy.McsData.RawData(file_path)
