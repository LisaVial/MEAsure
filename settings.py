import PyQt5.QtCore as QtCore
import json

from frequency_analysis.frequency_analysis_settings import FrequencyAnalysisSettings
from frequency_bands_analysis.frequency_bands_analysis_settings import FrequencyBandsAnalysisSettings
from spike_detection.spike_detection_settings import SpikeDetectionSettings
from filtering.filter_settings import FilterSettings
from plots.csd_plot.csd_plot_settings import CsdPlotSettings
from plots.ISI.isi_histogram_settings import IsiHistogramSettings
from plots.raster_plot.rasterplot_settings import RasterplotSettings
from spectrograms.spectrograms_settings import SpectrogramsSettings
from plots.plot_settings import PlotSettings


class Settings:

    instance = None

    def __init__(self):
        self.last_folder = ""
        self.main_window_geometry = bytearray()
        self.main_window_state = bytearray()
        self.spike_detection_settings = SpikeDetectionSettings()
        self.filter_settings = FilterSettings()
        self.rasterplot_settings = RasterplotSettings()
        self.csd_plot_settings = CsdPlotSettings()
        self.frequency_analysis_settings = FrequencyAnalysisSettings()
        self.frequency_bands_analysis_settings = FrequencyBandsAnalysisSettings()
        self.isi_histogram_settings = IsiHistogramSettings()
        self.spectrograms_settings = SpectrogramsSettings()
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
            if 'csd_plot_settings' in d.keys():
                self.csd_plot_settings.from_dict(d['csd_plot_settings'])
            if 'frequency_analysis_settings' in d.keys():
                self.frequency_analysis_settings.from_dict(d['frequency_analysis_settings'])
            if 'frequency_bands_analysis_settings' in d.keys():
                self.frequency_bands_analysis_settings.from_dict(d['frequency_bands_analysis_settings'])
            if 'isi_histogram_settings' in d.keys():
                self.frequency_analysis_settings.from_dict(d['frequency_analysis_settings'])
            if 'spectrograms_settings' in d.keys():
                self.spectrograms_settings.from_dict(d['spectrograms_settings'])
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
        d["frequency_analysis_settings"] = self.frequency_analysis_settings.to_dict()
        d["frequency_bands_analysis_settings"] = self.frequency_bands_analysis_settings.to_dict()
        d["isi_histogram_settings"] = self.isi_histogram_settings.to_dict()
        d["spectrograms_settings"] = self.spectrograms_settings.to_dict()
        return d

    def save(self, path):
        json.dump(self.to_dict(), path)
