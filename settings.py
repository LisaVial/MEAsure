import PyQt5.QtCore as QtCore
import json

from hilbert_transform.hilbert_transform_settings import HilbertTransformSettings
from frequency_analysis.frequency_analysis_settings import FrequencyAnalysisSettings
from frequency_bands_analysis.frequency_bands_analysis_settings import FrequencyBandsAnalysisSettings
from filtering.filter_settings import FilterSettings
from plots.heatmap.heatmap_settings import HeatmapSettings
from plots.ISI.isi_histogram_settings import IsiHistogramSettings
from plots.raster_plot.rasterplot_settings import RasterplotSettings
from plots.raw_trace_plot.raw_trace_settings import RawTraceSettings
from spectrograms.spectrograms_settings import SpectrogramsSettings


class Settings:

    instance = None

    def __init__(self):
        self.last_folder = ""
        self.main_window_geometry = bytearray()
        self.main_window_state = bytearray()
        self.filter_settings = FilterSettings()
        self.hilbert_transform_settings = HilbertTransformSettings()
        self.rasterplot_settings = RasterplotSettings()
        self.heatmap_settings = HeatmapSettings()
        self.frequency_analysis_settings = FrequencyAnalysisSettings()
        self.frequency_bands_analysis_settings = FrequencyBandsAnalysisSettings()
        self.isi_histogram_settings = IsiHistogramSettings()
        self.spectrograms_settings = SpectrogramsSettings()
        self.raw_trace_plot_settings = RawTraceSettings()
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
            if "hilbert_transform_settings" in d.keys():
                self.hilbert_transform_settings.from_dict(d["hilbert_transform_settings"])
            if "filter_settings" in d.keys():
                self.filter_settings.from_dict(d["filter_settings"])
            if "rasterplot_settings" in d.keys():
                self.rasterplot_settings.from_dict(d["rasterplot_settings"])
            if 'heatmap_settings' in d.keys():
                self.heatmap_settings.from_dict(d['heatmap_settings'])
            if 'frequency_analysis_settings' in d.keys():
                self.frequency_analysis_settings.from_dict(d['frequency_analysis_settings'])
            if 'frequency_bands_analysis_settings' in d.keys():
                self.frequency_bands_analysis_settings.from_dict(d['frequency_bands_analysis_settings'])
            if 'isi_histogram_settings' in d.keys():
                self.frequency_analysis_settings.from_dict(d['frequency_analysis_settings'])
            if 'spectrograms_settings' in d.keys():
                self.spectrograms_settings.from_dict(d['spectrograms_settings'])
            if 'raw_trace_plot_settings' in d.keys():
                self.raw_trace_plot_settings.from_dict(d['raw_trace_plot_settings'])
        except:
            pass

    def to_dict(self):
        d = dict()
        d["last_folder"] = self.last_folder
        d["main_window_geometry"] = bytearray(self.main_window_geometry).decode("ascii")
        d["main_window_state"] = bytearray(self.main_window_state).decode("ascii")
        d["hilbert_transform_settings"] = self.hilbert_transform_settings.to_dict()
        d["filter_settings"] = self.filter_settings.to_dict()
        d["rasterplot_settings"] = self.rasterplot_settings.to_dict()
        d["heatmap_settings"] = self.heatmap_settings.to_dict()
        d["frequency_analysis_settings"] = self.frequency_analysis_settings.to_dict()
        d["frequency_bands_analysis_settings"] = self.frequency_bands_analysis_settings.to_dict()
        d["isi_histogram_settings"] = self.isi_histogram_settings.to_dict()
        d["spectrograms_settings"] = self.spectrograms_settings.to_dict()
        d["raw_trace_plot_settings"] = self.raw_trace_plot_settings.to_dict()
        return d

    def save(self, path):
        json.dump(self.to_dict(), path)
