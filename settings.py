import PyQt5.QtCore as QtCore
import json

from spike_detection.spike_detection_settings import SpikeDetectionSettings
from filtering.filter_settings import FilterSettings
from plots.raster_plot.rasterplot_settings import RasterplotSettings

class Settings:

    instance = None

    def __init__(self):
        self.last_folder = ""
        self.main_window_geometry = bytearray()
        self.main_window_state = bytearray()
        self.spike_detection_settings = SpikeDetectionSettings()
        self.filter_settings = FilterSettings()
        self.rasterplot_settings = RasterplotSettings()
        Settings.instance = self

    def load_settings_from_file(self, path):
        try:
            d = json.load(path)
            if "last_folder" in d.keys():
                self.last_folder = d["last_folder"]
            if "main_window_geometry" in d.keys():
                self.main_window_geometry = QtCore.QByteArray(bytearray(d["main_window_geometry"], "ascii"))
            if "main_window_state" in d.keys():
                self.main_window_state = QtCore.QByteArray(bytearray(d["main_window_state"], "ascii"))
            if "spike_detection_settings" in d.keys():
                self.spike_detection_settings.from_dict(d["spike_detection_settings"])
            if "filter_settings" in d.keys():
                self.filter_settings.from_dict(d["filter_settings"])
            if "rasterplot_settings" in d.keys():
                self.rasterplot_settings.from_dict(d["rasterplot_settings"])
        except:
            pass

    def to_dict(self):
        d = dict()
        d["last_folder"] = self.last_folder
        d["main_window_geometry"] = bytearray(self.main_window_geometry).decode("ascii")
        d["main_window_state"] = bytearray(self.main_window_state).decode("ascii")
        d["spike_detection_settings"] = self.spike_detection_settings.to_dict()
        d["filter_settings"] = self.filter_settings.to_dict()
        d["rasterplot_settings"] = self.rasterplot_settings.to_dict()
        return d

    def save(self, path):
        json.dump(self.to_dict(), path)