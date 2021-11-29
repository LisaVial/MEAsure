from PyQt5 import QtWidgets, QtGui, QtCore

# all the following imports are script of the MEAsure application
from file_handling.mcs_data_reader import McsDataReader
from file_handling.SC_data_reader import SCDataReader

from results import ResultStoring
from mea_grid import MeaGrid

from settings import Settings
from file_manager import FileManager

from filtering.filter_settings_dialog import FilterSettingsDialog
from filtering.filter_settings import FilterSettings
from filtering.filter_tab import FilterTab

from hilbert_transform.hilbert_transform_tab import HilbertTransformTab
from hilbert_transform.hilbert_transform_settings import HilbertTransformSettings
from hilbert_transform.hilbert_transform_settings_dialog import HilbertTransformSettingsDialog

from plots.raw_trace_plot.raw_trace_settings import RawTraceSettings
from plots.raw_trace_plot.raw_trace_plot_tab import RawTracePlotTab
from plots.raw_trace_plot.raw_trace_settings_dialog import RawTraceSettingsDialog

from frequency_analysis.frequency_analysis_settings_dialog import FrequencyAnalysisSettingsDialog
from frequency_analysis.frequency_analysis_settings import FrequencyAnalysisSettings
from frequency_analysis.frequency_analysis_tab import FrequencyAnalysisTab

from frequency_bands_analysis.frequency_bands_analysis_settings_dialog import FrequencyBandsAnalysisSettingsDialog
from frequency_bands_analysis.frequency_bands_analysis_settings import FrequencyBandsAnalysisSettings
from frequency_bands_analysis.frequency_bands_tab import FrequencyBandsTab

from spectrograms.spectrograms_tab import SpectrogramsTab
from spectrograms.spectrograms_settings import SpectrogramsSettings
from spectrograms.spectrograms_settings_dialog import SpectrogramsSettingsDialog

from burst_detection.burst_detection_tab import BurstDetectionTab
from burst_detection.burst_detection_settings import BurstDetectionSettings
from burst_detection.burst_detection_settings_dialog import BurstDetectionSettingsDialog

from plots.raster_plot.rasterplot_tab import RasterplotTab
from plots.raster_plot.rasterplot_settings_dialog import RasterplotSettingsDialog
from plots.raster_plot.rasterplot_settings import RasterplotSettings

from plots.heatmap.heatmap_tab import HeatmapTab
from plots.heatmap.heatmap_settings_dialog import HeatmapSettingsDialog
from plots.heatmap.heatmap_settings import HeatmapSettings

from plots.ISI.isi_histogram_tab import IsiHistogramTab
from plots.ISI.isi_histogram_settings import IsiHistogramSettings
from plots.ISI.isi_histogram_settings_dialog import IsiHistogramSettingsDialog

from spike_check.spike_check_dialog import SpikeCheckDialog

from utility.worker_thread import WorkerThread


# the MeaFileView Widget is portraying the currently selected Mea recording and what the user can do with it
class MeaFileView(QtWidgets.QWidget):
    def __init__(self, parent, mea_file):
        super().__init__(parent)
        self.mea_file = mea_file    # this is just the path to the current mea recording h5 file
        self.results = ResultStoring()
        self.reader = None
        self.worker_thread = WorkerThread(self)
        self.worker_thread.finished.connect(self.on_worker_thread_finished)
        self.worker_thread.set_function(self.initialize_reader)
        self.worker_thread.start()
        # start animation
        QtWidgets.QApplication.instance().main_window.animation_overlay.start()
        self.file_manager = None
        self.hilbert_transform_settings = None
        self.frequency_analysis_settings = None
        self.frequency_band_analysis_settings = None
        self.filter_settings = None
        self.rasterplot_settings = None
        self.spike_detection_settings = None
        self.csd_plot_settings = None
        self.heatmap_settings = None
        self.isi_histogram_settings = None
        self.spectrograms_settings = None
        self.raw_trace_plot_settings = None
        self.burst_detection_settings = None

        self.toolbar = None

        self.show_file_manager = None
        self.show_mea_grid = None
        self.show_raw_trace_plot_dialog = None
        self.show_hilbert_transform_tab = None
        self.show_filter_dialog = None
        self.show_spike_detection_dialog = None
        self.add_frequency_analysis_tab = None
        self.add_frequency_bands_analysis_tab = None
        self.add_spectrogram_tab = None
        self.add_csd_plot_tab = None
        self.add_rasterplot_tab = None
        self.add_isi_histogram_tab = None
        self.add_heatmap_tab = None
        self.open_burst_detection_tab = None
        self.open_spike_check = None
        self.mea_grid = None
        self.tab_widget = None

        self.filter_tab = None
        self.hilbert_transform_tab = None
        self.raw_trace_tab = None
        self.frequency_analysis_tab = None
        self.frequency_bands_analysis_tab = None
        self.spectrograms_tab = None
        self.burst_detection_tab = None
        self.isi_histogram_tab = None
        self.heatmap_tab = None
        self.rasterplot_tab = None

        self.mcs_channel_ids = None
        self.mcs_channel_labels = None

    # the initialisation of this class is divided in two parts, i am not completely happy with it, but it was
    # necessary to get the loading screen animation (dancing neuron) in there
    def continue_initialisation(self):
        self.file_manager = FileManager(self, self.reader.filename)  # this widget handles tasks in respect to
        # filepaths, with it the user is able to chose the .meae filepath (just .h5 data after analysis) or the
        # filepath of results of spyking circus

        # here, settings for different tasks which can be carried out by the user are defined
        self.hilbert_transform_settings = Settings.instance.hilbert_transform_settings
        self.frequency_analysis_settings = Settings.instance.frequency_analysis_settings
        self.frequency_band_analysis_settings = Settings.instance.frequency_bands_analysis_settings
        self.filter_settings = Settings.instance.filter_settings
        self.rasterplot_settings = Settings.instance.rasterplot_settings
        self.heatmap_settings = Settings.instance.heatmap_settings
        self.isi_histogram_settings = Settings.instance.isi_histogram_settings
        self.spectrograms_settings = Settings.instance.spectrograms_settings
        self.raw_trace_plot_settings = Settings.instance.raw_trace_plot_settings
        self.burst_detection_settings = Settings.instance.burst_detection_settings

        # setting up the main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        # here, we set up a toolbar, which holds different buttons to start executing different tasks
        self.toolbar = QtWidgets.QToolBar(self)
        # this function only is for bigger icons
        self.toolbar.setIconSize(QtCore.QSize(52, 52))

        # the first task is just to show the file manager
        # with toolbars we actually have to set up QAction
        self.show_file_manager = QtWidgets.QAction("File manager", self)
        # here we set the icon for the action
        file_manager_icon = QtGui.QIcon("./icons/file_manager_icon.png")
        self.show_file_manager.setIcon(file_manager_icon)
        # we have to connect the QAction has to be connected to a function which tells the program what to do
        self.show_file_manager.triggered.connect(self.on_show_file_manager)
        self.show_file_manager.setCheckable(True)
        self.show_file_manager.setChecked(False)
        self.toolbar.addAction(self.show_file_manager)

        self.show_mea_grid = QtWidgets.QAction("MEA grid", self)
        mea_grid_icon = QtGui.QIcon("./icons/mea_grid_icon.png")
        self.show_mea_grid.setIcon(mea_grid_icon)
        self.show_mea_grid.triggered.connect(self.on_show_mea_grid)
        self.show_mea_grid.setCheckable(True)
        self.show_mea_grid.setChecked(True)
        self.toolbar.addAction(self.show_mea_grid)

        self.show_filter_dialog = QtWidgets.QAction("Filtering", self)
        self.show_filter_dialog.triggered.connect(self.open_filter_dialog)
        filter_icon = QtGui.QIcon("./icons/filter_icon.png")
        self.show_filter_dialog.setIcon(filter_icon)
        self.toolbar.addAction(self.show_filter_dialog)

        self.show_hilbert_transform_tab = QtWidgets.QAction('Hilbert Transform', self)
        self.show_hilbert_transform_tab.triggered.connect(self.open_hilbert_transform_tab)
        hilbert_transform_icon = QtGui.QIcon('./icons/hilbert_transform_icon.png')
        self.show_hilbert_transform_tab.setIcon(hilbert_transform_icon)
        self.toolbar.addAction(self.show_hilbert_transform_tab)

        self.show_raw_trace_plot_dialog = QtWidgets.QAction('Raw trace plot', self)
        self.show_raw_trace_plot_dialog.triggered.connect(self.open_raw_trace_plot_dialog)
        raw_trace_plot_icon = QtGui.QIcon('./icons/raw_trace_icon.png')
        self.show_raw_trace_plot_dialog.setIcon(raw_trace_plot_icon)
        self.toolbar.addAction(self.show_raw_trace_plot_dialog)

        self.add_frequency_analysis_tab = QtWidgets.QAction('Frequency analysis', self)
        frequency_analysis_icon = QtGui.QIcon("./icons/frequency_analysis_icon.png")
        self.add_frequency_analysis_tab.setIcon(frequency_analysis_icon)
        self.add_frequency_analysis_tab.triggered.connect(self.open_frequency_analysis_settings)
        self.toolbar.addAction(self.add_frequency_analysis_tab)

        self.add_frequency_bands_analysis_tab = QtWidgets.QAction('Analysis of cortical frequency bands', self)
        cortical_bands_analysis_icon = QtGui.QIcon("./icons/frequency_bands_analysis_icon.png")
        self.add_frequency_bands_analysis_tab.setIcon(cortical_bands_analysis_icon)
        self.add_frequency_bands_analysis_tab.triggered.connect(self.open_frequency_bands_analysis_tab_settings)
        self.toolbar.addAction(self.add_frequency_bands_analysis_tab)

        self.add_spectrogram_tab = QtWidgets.QAction('Spectrograms', self)
        spectrograms_icon = QtGui.QIcon("./icons/spectrograms_icon.png")
        self.add_spectrogram_tab.setIcon(spectrograms_icon)
        self.add_spectrogram_tab.triggered.connect(self.open_spectograms_settings_dialog)
        self.toolbar.addAction(self.add_spectrogram_tab)

        self.add_rasterplot_tab = QtWidgets.QAction('Rasterplot', self)
        rasterplot_plot_icon = QtGui.QIcon("./icons/rasterplot_icon.png")
        self.add_rasterplot_tab.setIcon(rasterplot_plot_icon)
        self.add_rasterplot_tab.triggered.connect(self.open_rasterplot_settings_dialog)
        self.toolbar.addAction(self.add_rasterplot_tab)

        self.add_isi_histogram_tab = QtWidgets.QAction('ISI Histogram', self)
        isi_histogram_icon = QtGui.QIcon("./icons/isi_histogram_icon.png")
        self.add_isi_histogram_tab.setIcon(isi_histogram_icon)
        self.add_isi_histogram_tab.triggered.connect(self.open_isi_histogram_settings_dialog)
        self.toolbar.addAction(self.add_isi_histogram_tab)

        self.add_heatmap_tab = QtWidgets.QAction('Heatmap', self)
        heatmap_icon = QtGui.QIcon("./icons/heatmap_icon.png")
        self.add_heatmap_tab.setIcon(heatmap_icon)
        self.add_heatmap_tab.triggered.connect(self.open_heatmap_settings_dialog)
        self.toolbar.addAction(self.add_heatmap_tab)

        self.open_burst_detection_tab = QtWidgets.QAction('Burst Detection', self)
        burst_detection_icon = QtGui.QIcon("./icons/burst_detection_icon.png")
        self.open_burst_detection_tab.setIcon(burst_detection_icon)
        self.open_burst_detection_tab.triggered.connect(self.open_burst_detection_settings_dialog)
        self.toolbar.addAction(self.open_burst_detection_tab)

        self.open_spike_check = QtWidgets.QAction('Spike Verfication', self)
        spike_verification_icon = QtGui.QIcon("./icons/spike_verification_icon.png")
        self.open_spike_check.setIcon(spike_verification_icon)
        self.open_spike_check.triggered.connect(self.open_spike_check_dialog)
        self.toolbar.addAction(self.open_spike_check)

        main_layout.addWidget(self.toolbar)

        sub_layout = QtWidgets.QHBoxLayout(self)
        sub_layout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        mea_grid_and_minor_widgets_layout = QtWidgets.QVBoxLayout(self)
        mea_grid_and_minor_widgets_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        mea_grid_and_minor_widgets_layout.addWidget(self.file_manager)
        self.mea_grid = MeaGrid(self)
        self.mea_grid.setFixedSize(600, 600)
        mea_grid_and_minor_widgets_layout.addWidget(self.mea_grid)
        sub_layout.addLayout(mea_grid_and_minor_widgets_layout)

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabBarAutoHide(False)
        self.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)

        sub_layout.addWidget(self.tab_widget)
        main_layout.addLayout(sub_layout)

        # make sure widget visibility matches tool bar button check states
        self.file_manager.setVisible(self.show_file_manager.isChecked())
        self.mea_grid.setVisible(self.show_mea_grid.isChecked())

        self.mcs_channel_ids = self.reader.channel_ids
        self.mcs_channel_labels = self.reader.labels

    def initialize_reader(self):
        self.reader = McsDataReader(self.mea_file)

    @QtCore.pyqtSlot()
    def on_worker_thread_finished(self):
        QtWidgets.QApplication.instance().main_window.animation_overlay.stop()
        self.continue_initialisation()

    def open_hilbert_transform_tab(self):
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_channel_modes = [HilbertTransformSettings.ChannelSelection.ALL]
        if len(channel_labels_and_indices) > 0:
            allowed_channel_modes.append(HilbertTransformSettings.ChannelSelection.SELECTION)
        settings_dialog = HilbertTransformSettingsDialog(self, allowed_channel_modes, self.hilbert_transform_settings)
        if settings_dialog.exec() == 1:
            self.hilbert_transform_settings = settings_dialog.get_settings()
            if self.hilbert_transform_settings.channel_selection == HilbertTransformSettings.ChannelSelection.ALL:
                grid_labels = self.reader.get_channel_ids()[1]
            elif self.hilbert_transform_settings.channel_selection == HilbertTransformSettings.ChannelSelection.SELECTION:
                grid_labels_and_indices = self.mea_grid.get_selected_channels()
                grid_labels = [values[0] for values in grid_labels_and_indices]
            Settings.instance.hilbert_transform_settings = self.hilbert_transform_settings
            self.hilbert_transform_tab = HilbertTransformTab(self, self.reader, grid_labels,
                                                             self.hilbert_transform_settings)
            self.tab_widget.addTab(self.hilbert_transform_tab, 'Hilbert Transform Tab')

    def open_raw_trace_plot_dialog(self):
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_channel_modes = [RawTraceSettings.ChannelSelection.ALL]
        if len(channel_labels_and_indices) > 0:
            allowed_channel_modes.append(RawTraceSettings.ChannelSelection.SELECTION)
        settings_dialog = RawTraceSettingsDialog(self, allowed_channel_modes, self.reader.duration,
                                                 self.raw_trace_plot_settings)
        if settings_dialog.exec() == 1:
            self.raw_trace_plot_settings = settings_dialog.get_settings()
            if self.raw_trace_plot_settings.channel_selection == RawTraceSettings.ChannelSelection.ALL:
                grid_labels = self.reader.labels
                # probably this is wrong and also should be the ordered ids
                grid_indices = range(len(self.reader.voltage_traces))
            elif self.raw_trace_plot_settings.channel_selection == RawTraceSettings.ChannelSelection.SELECTION:
                grid_labels_and_indices = self.mea_grid.get_selected_channels()
                grid_labels = [values[0] for values in grid_labels_and_indices]
                grid_indices = [values[1] for values in grid_labels_and_indices]
            Settings.instance.raw_trace_plot_settings = self.raw_trace_plot_settings
            sampling_rate = self.reader.sampling_frequency
            self.raw_trace_tab = RawTracePlotTab(self, self.reader, self.raw_trace_plot_settings, grid_labels,
                                                 grid_indices, sampling_rate)
            self.tab_widget.addTab(self.raw_trace_tab, 'Raw trace plot')

    @QtCore.pyqtSlot()
    def open_filter_dialog(self):
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_modes = [FilterSettings.ChannelSelection.ALL]
        if len(channel_labels_and_indices) > 0:
            allowed_modes.append(FilterSettings.ChannelSelection.SELECTION)
        settings_dialog = FilterSettingsDialog(self, allowed_modes, self.filter_settings)
        if settings_dialog.exec() == 1:  # 'Execute' clicked
            self.filter_settings = settings_dialog.get_settings()
            if self.filter_settings.channel_selection == FilterSettings.ChannelSelection.ALL:
                grid_indices = range(len(self.reader.voltage_traces))
                grid_labels = self.reader.labels
            elif self.filter_settings.channel_selection == FilterSettings.ChannelSelection.SELECTION:
                grid_labels_and_indices = self.mea_grid.get_selected_channels()
                grid_indices = [values[1] for values in grid_labels_and_indices]
                grid_labels = [values[0] for values in grid_labels_and_indices]
            # overwrite global settings as well
            Settings.instance.filter_settings = self.filter_settings

            # initialise filtering
            # give FilterThread indices (all is default and if selected, thread has to receive special indices
            # -> via filter tab?)
            self.filter_tab = FilterTab(self, self.reader, grid_indices, grid_labels, self.filter_settings)
            self.tab_widget.addTab(self.filter_tab, "Filtering")
            self.filter_tab.initialize_filtering()

    def open_isi_histogram_settings_dialog(self, is_pressed):
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_channel_modes = [IsiHistogramSettings.ChannelSelection.ALL]
        if len(channel_labels_and_indices) > 0:
            allowed_channel_modes.append(IsiHistogramSettings.ChannelSelection.SELECTION)
            # determine allowed modes
        allowed_modes = [IsiHistogramSettings.Mode.MCS]
        if self.file_manager.get_verified_meae_file() is not None:
            allowed_modes.append(IsiHistogramSettings.Mode.MEAE)
        if self.file_manager.get_verified_sc_file() is not None:
            allowed_modes.append(IsiHistogramSettings.Mode.SC)
        settings_dialog = IsiHistogramSettingsDialog(self, allowed_modes, allowed_channel_modes,
                                                     self.isi_histogram_settings)
        if settings_dialog.exec() == 1:  # 'Execute' clicked
            self.plot_settings = settings_dialog.get_settings()
            # overwrite global settings as well
            if self.plot_settings.channel_selection == IsiHistogramSettings.ChannelSelection.ALL:
                grid_labels = self.reader.labels
                grid_indices = self.reader.channel_ids
            elif self.plot_settings.channel_selection == IsiHistogramSettings.ChannelSelection.SELECTION:
                grid_labels_and_indices = self.mea_grid.get_selected_channels()
                grid_labels = [values[0] for values in grid_labels_and_indices]
                grid_indices = [values[1] for values in grid_labels_and_indices]

            Settings.instance.isi_histogram_settings = self.plot_settings
            sampling_rate = self.reader.sampling_frequency

            # initialise plotting
            if self.plot_settings.mode == IsiHistogramSettings.Mode.MCS:
                self.isi_histogram_tab = IsiHistogramTab(self, self.reader, self.plot_settings, sampling_rate,
                                                         grid_labels, grid_indices)
                self.tab_widget.addTab(self.isi_histogram_tab, "ISI Histogram")
            elif self.plot_settings.mode == IsiHistogramSettings.Mode.MEAE:
                meae_path = self.file_manager.get_verified_meae_file()
                self.isi_histogram_tab = IsiHistogramTab(self, self.reader, self.plot_settings, sampling_rate,
                                                         grid_labels, grid_indices)
                self.tab_widget.addTab(self.isi_histogram_tab, "ISI Histogram")
            elif self.plot_settings.mode == IsiHistogramSettings.Mode.SC:
                sc_path = self.file_manager.get_verified_sc_file()
                sc_base_filepath = self.file_manager.get_verified_sc_base_file()
                sc_reader = SCDataReader(sc_path, sc_base_filepath)
                self.isi_histogram_tab = IsiHistogramTab(self, sc_reader, self.plot_settings, sampling_rate,
                                                         grid_labels, grid_indices)
                self.tab_widget.addTab(self.isi_histogram_tab, "ISI Histogram")

    def open_frequency_analysis_settings(self, is_pressed):
        # for portrayal reasons, there should be a maximum of 16 channels (one column) per plot
        # if more channels are selected, the wisest thing would be to open several plots simultaneously
        # maybe this approach could also be used for rasterplots and isi histograms
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_channel_modes = [FrequencyAnalysisSettings.ChannelSelection.ALL]
        if len(channel_labels_and_indices) > 0:
            allowed_channel_modes.append(FrequencyAnalysisSettings.ChannelSelection.SELECTION)
        settings_dialog = FrequencyAnalysisSettingsDialog(self, allowed_channel_modes, self.frequency_analysis_settings)
        if settings_dialog.exec() == 1:
            self.frequency_analysis_settings = settings_dialog.get_settings()
            Settings.instance.frequency_analysis_settings = self.frequency_analysis_settings
            if self.frequency_analysis_settings.channel_selection == FrequencyAnalysisSettings.ChannelSelection.ALL:
                grid_indices = range(len(self.reader.voltage_traces))
                grid_labels = self.reader.labels
            elif self.frequency_analysis_settings.channel_selection == FrequencyAnalysisSettings.ChannelSelection.SELECTION:
                grid_labels_and_indices = self.mea_grid.get_selected_channels()
                grid_indices = [values[1] for values in grid_labels_and_indices]
                grid_labels = [values[0] for values in grid_labels_and_indices]
            self.frequency_analysis_tab = FrequencyAnalysisTab(self, self.reader, grid_indices, grid_labels,
                                                               self.frequency_analysis_settings)
            self.tab_widget.addTab(self.frequency_analysis_tab, "Frequency Analysis")
            self.frequency_analysis_tab.initialize_frequency_analysis()

    def open_frequency_bands_analysis_tab_settings(self, is_pressed):
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_channel_modes = [FrequencyBandsAnalysisSettings.ChannelSelection.ALL]

        if len(channel_labels_and_indices) > 0:
            allowed_channel_modes.append(FrequencyBandsAnalysisSettings.ChannelSelection.SELECTION)
        settings_dialog = FrequencyBandsAnalysisSettingsDialog(self, allowed_channel_modes,
                                                               self.frequency_band_analysis_settings)
        if settings_dialog.exec() == 1:
            self.frequency_band_analysis_settings = settings_dialog.get_settings()
            Settings.instance.frequency_band_analysis_settings = self.frequency_band_analysis_settings
            if self.frequency_band_analysis_settings.channel_selection == \
                    FrequencyBandsAnalysisSettings.ChannelSelection.ALL:
                grid_indices = range(len(self.reader.voltage_traces))
                grid_labels = self.reader.labels.copy()
            elif self.frequency_band_analysis_settings.channel_selection == \
                    FrequencyBandsAnalysisSettings.ChannelSelection.SELECTION:
                grid_labels_and_indices = self.mea_grid.get_selected_channels()
                grid_indices = [values[1] for values in grid_labels_and_indices]
                grid_labels = [values[0] for values in grid_labels_and_indices]
            self.frequency_bands_analysis_tab = FrequencyBandsTab(self, self.reader, grid_indices, grid_labels,
                                                                  self.frequency_band_analysis_settings)
            self.tab_widget.addTab(self.frequency_bands_analysis_tab, "Frequency Band Analysis")
            self.frequency_bands_analysis_tab.initialize_frequency_bands_analysis()

    def open_spectograms_settings_dialog(self, is_pressed):
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_channel_modes = [SpectrogramsSettings.ChannelSelection.ALL]

        if len(channel_labels_and_indices) > 0:
            allowed_channel_modes.append(SpectrogramsSettings.ChannelSelection.SELECTION)
        settings_dialog = SpectrogramsSettingsDialog(self, allowed_channel_modes, self.spectrograms_settings)

        if settings_dialog.exec() == 1:
            self.spectrograms_settings = settings_dialog.get_settings()
            Settings.instance.spectrograms_settings = self.spectrograms_settings
        if self.spectrograms_settings.channel_selection == SpectrogramsSettings.ChannelSelection.ALL:
            grid_indices = range(len(self.reader.voltage_traces))
            grid_labels = self.reader.labels
        elif self.spectrograms_settings.channel_selection == SpectrogramsSettings.ChannelSelection.SELECTION:
            grid_labels_and_indices = self.mea_grid.get_selected_channels()
            grid_indices = [values[1] for values in grid_labels_and_indices]
            grid_labels = [values[0] for values in grid_labels_and_indices]
        self.spectrograms_tab = SpectrogramsTab(self, self.reader, grid_indices, grid_labels,
                                                self.spectrograms_settings)
        self.spectrograms_tab.initialize_spectrogram_calculation()
        self.tab_widget.addTab(self.spectrograms_tab, "Spectrograms")

    def open_heatmap_settings_dialog(self, is_pressed):
        # get main window from application (set in start_gui.py)
        main_window = QtWidgets.QApplication.instance().main_window

        allowed_modes = [HeatmapSettings.Mode.MCS]
        if self.file_manager.get_verified_meae_file() is not None:
            allowed_modes.append(HeatmapSettings.Mode.MEAE)
        if self.file_manager.get_verified_sc_file() is not None:
            allowed_modes.append(HeatmapSettings.Mode.SC)
        settings_dialog = HeatmapSettingsDialog(self, allowed_modes, self.heatmap_settings, main_window.get_heatmaps())
        if settings_dialog.exec() == 1:  # 'Execute' clicked
            self.heatmap_settings = settings_dialog.get_settings()
            # overwrite global settings as well
            Settings.instance.plot_settings = self.heatmap_settings

            # initialise plotting
            if self.heatmap_settings.mode == HeatmapSettings.Mode.MCS:
                self.heatmap_tab = HeatmapTab(self, self.reader, self.mcs_channel_ids, self.heatmap_settings)
                self.tab_widget.addTab(self.heatmap_tab, "Heatmap")
            elif self.heatmap_settings.mode == HeatmapSettings.Mode.MEAE:
                meae_path = self.file_manager.get_verified_meae_file()
                self.heatmap_tab = HeatmapTab(self, self.reader, self.mcs_channel_ids, self.heatmap_settings)
                self.tab_widget.addTab(self.heatmap_tab, "Heatmap")
            elif self.heatmap_settings.mode == HeatmapSettings.Mode.SC:
                sc_path = self.file_manager.get_verified_sc_file()
                sc_base_filepath = self.file_manager.get_verified_sc_base_file()
                sc_reader = SCDataReader(sc_path, sc_base_filepath)
                self.heatmap_tab = HeatmapTab(self, sc_reader, self.mcs_channel_labels, self.mcs_channel_ids,
                                              self.heatmap_settings)
                self.tab_widget.addTab(self.heatmap_tab, "Heatmap")

    def open_rasterplot_settings_dialog(self, is_pressed):
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_channel_modes = [RasterplotSettings.ChannelSelection.ALL]
        if len(channel_labels_and_indices) > 0:
            allowed_channel_modes.append(RasterplotSettings.ChannelSelection.SELECTION)

        # determine allowed modes
        allowed_modes = [RasterplotSettings.Mode.MCS]
        if self.file_manager.get_verified_meae_file() is not None:
            allowed_modes.append(RasterplotSettings.Mode.MEAE)
        if self.file_manager.get_verified_sc_file() is not None:
            allowed_modes.append(RasterplotSettings.Mode.SC)
        settings_dialog = RasterplotSettingsDialog(self, allowed_modes, allowed_channel_modes, self.rasterplot_settings)
        if settings_dialog.exec() == 1:  # 'Execute' clicked
            self.plot_settings = settings_dialog.get_settings()
            # overwrite global settings as well
            if self.plot_settings.channel_selection == RasterplotSettings.ChannelSelection.ALL:
                grid_labels = self.reader.labels
                grid_indices = self.reader.channel_ids
            elif self.plot_settings.channel_selection == RasterplotSettings.ChannelSelection.SELECTION:
                grid_labels_and_indices = self.mea_grid.get_selected_channels()
                grid_labels = [values[0] for values in grid_labels_and_indices]
                grid_indices = [values[1] for values in grid_labels_and_indices]

            Settings.instance.raserplot_settings = self.plot_settings
            sampling_rate = self.reader.sampling_frequency
            duration = self.reader.duration

            # initialise plotting
            if self.plot_settings.mode == RasterplotSettings.Mode.MCS:
                self.rasterplot_tab = RasterplotTab(self, self.reader, self.plot_settings, sampling_rate, duration,
                                                    grid_labels, grid_indices, self.mcs_channel_ids)
                self.tab_widget.addTab(self.rasterplot_tab, "Rasterplot")
            elif self.plot_settings.mode == RasterplotSettings.Mode.MEAE:
                meae_path = self.file_manager.get_verified_meae_file()
                self.rasterplot_tab = RasterplotTab(self, self.reader, self.plot_settings, sampling_rate, duration,
                                                    grid_labels, grid_indices, self.mcs_channel_ids)
                self.tab_widget.addTab(self.rasterplot_tab, "Rasterplot")
            elif self.plot_settings.mode == RasterplotSettings.Mode.SC:
                sc_path = self.file_manager.get_verified_sc_file()
                sc_base_filepath = self.file_manager.get_verified_sc_base_file()
                sc_reader = SCDataReader(sc_path, sc_base_filepath)
                self.rasterplot_tab = RasterplotTab(self, sc_reader, self.plot_settings, sampling_rate, duration,
                                                    grid_labels, grid_indices)
                self.tab_widget.addTab(self.rasterplot_tab, "Rasterplot")

    def open_burst_detection_settings_dialog(self):
        channel_labels_and_indices = self.mea_grid.get_selected_channels()
        allowed_channel_modes = [BurstDetectionSettings.ChannelSelection.ALL]
        if len(channel_labels_and_indices) > 0:
            allowed_channel_modes.append(BurstDetectionSettings.ChannelSelection.SELECTION)

        # instead of giving the user the allowed modes, i will only consider spyking circus spiketimes
        settings_dialog = BurstDetectionSettingsDialog(self, allowed_channel_modes, self.burst_detection_settings)
        if settings_dialog.exec() == 1:
            self.burst_detection_settings = settings_dialog.get_settings()
            if self.burst_detection_settings.channel_selection == BurstDetectionSettings.ChannelSelection.ALL:
                grid_labels = self.reader.labels
                grid_indices = self.reader.channel_ids
            elif self.burst_detection_settings.channel_selection == BurstDetectionSettings.ChannelSelection.SELECTION:
                grid_labels_and_indices = self.mea_grid.get_selected_channels()
                grid_labels = [values[0] for values in grid_labels_and_indices]
                grid_indices = [values[1] for values in grid_labels_and_indices]

            Settings.instance.burst_detection_settings = self.burst_detection_settings
            sc_path = self.file_manager.get_verified_sc_file()
            sc_base_filepath = self.file_manager.get_verified_sc_base_file()
            sc_reader = SCDataReader(sc_path, sc_base_filepath)
            self.burst_detection_tab = BurstDetectionTab(self, self.reader, sc_reader, grid_labels, grid_indices,
                                                         self.burst_detection_settings)
            self.tab_widget.addTab(self.burst_detection_tab, 'Burst Detection')
            self.burst_detection_tab.initialize_burst_detection()

    def open_spike_check_dialog(self, is_pressed):
        sc_filepath = self.file_manager.get_verified_sc_file()
        sc_base_filepath = self.file_manager.get_verified_sc_base_file()
        if sc_filepath and sc_base_filepath:
            sc_reader = SCDataReader(sc_filepath, sc_base_filepath)
            spike_check_dialog = SpikeCheckDialog(self, self.reader, sc_reader)
            spike_check_dialog.exec()
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Please set spyking circus result and base file first')
            error_dialog.exec_()

    def on_show_file_manager(self, is_pressed):
        self.file_manager.setVisible(is_pressed)

    def on_show_mea_grid(self, is_pressed):
        self.mea_grid.setVisible(is_pressed)

    @QtCore.pyqtSlot(int)
    def on_tab_close_requested(self, index):
        # get tab that should be closed
        tab = self.tab_widget.widget(index)
        # tab can be FilterTab, FrequencyAnalysisTab, etc.
        # the important thing is that the tab has a can_be_closed method
        if tab.can_be_closed():
            self.tab_widget.removeTab(index)
        # else: do not close tab because it is busy (= ignore close request)

    def can_be_closed(self):
        tab_count = self.tab_widget.count()

        # check if all tabs can be closed
        can_all_tabs_be_closed = True
        for tab_index in range(tab_count):
            tab = self.tab_widget.widget(tab_index)
            if not tab.can_be_closed():
                can_all_tabs_be_closed = False
                break

        return can_all_tabs_be_closed
