import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from spike_check.channel_selection_widget import ChannelSelectionWidget
from spike_check.raw_trace_w_threshold_plot import RawTraceWThresholdPlot
from spike_check.voltage_trace_histogram_plot import VoltageTraceHistogramPlot
from spike_check.spike_time_plot import SpikeTimePlot
from spike_check.navigation_buttons_widget import NavigationButtonsWidget
from spike_check.spike_sorting_plot import SpikeSortingPlot

from utility.channel_utility import ChannelUtility


class SpikeCheckDialog(QtWidgets.QDialog):
    def __init__(self, parent, mcs_reader, sc_reader):
        super().__init__(parent)

        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.st_index = 0

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)

        self.setWindowTitle("Verification of detected spikes")

        main_layout = QtWidgets.QGridLayout(self)

        # insert widget to select channel for which spikes should be checked
        channel_selection_widget = ChannelSelectionWidget(self)
        channel_selection_widget.channel_selection_changed.connect(self.on_channel_selection_changed)
        main_layout.addWidget(channel_selection_widget, 0, 0, 1, 2)
        self.label = channel_selection_widget.label
        self.label_index = ChannelUtility.get_ordered_index(self.label)

        # insert plot widget that shows raw trace of channel: Plot title should show channel label, plot should show
        #   raw trace and thresholds (maybe get settings)
        self.raw_trace_plot_widget = RawTraceWThresholdPlot(self, self.mcs_reader, self.sc_reader, self.label,
                                                            self.label_index)
        main_layout.addWidget(self.raw_trace_plot_widget, 1, 0)

        self.histogram_plot_widget = VoltageTraceHistogramPlot(self, self.mcs_reader, self.sc_reader, self.label,
                                                               self.label_index)
        main_layout.addWidget(self.histogram_plot_widget, 1, 1)

        # insert a plot widget which shows 10 ms around a spike (it would be great if the spiketime is also indicated in
        #   the first plot widget)
        self.spike_time_plot_widget = SpikeTimePlot(self, self.mcs_reader, self.sc_reader, self.label, self.label_index)
        main_layout.addWidget(self.spike_time_plot_widget, 2, 0)
        self.spike_sorting_plot_widget = SpikeSortingPlot(self, self.mcs_reader, self.sc_reader, self.label)
        main_layout.addWidget(self.spike_sorting_plot_widget, 2, 1)
        #
        # # buttons on the bottom of the dialog to navigate through spike times
        max_idx = len(self.sc_reader.spiketimes[self.label_index]) - 1
        self.navigation_buttons_widget = NavigationButtonsWidget(self, max_idx)
        main_layout.addWidget(self.navigation_buttons_widget, 3, 0, 1, 2)
        self.navigation_buttons_widget.index_changed.connect(self.on_spiketime_index_changed)
        #

        # make first column twice as wide as the second one
        main_layout.setColumnStretch(0, 2)
        main_layout.setColumnStretch(1, 1)
        self.histogram_plot_widget.plot(self.label_index)
        self.raw_trace_plot_widget.plot(self.label)
        if self.label_index not in self.sc_reader.dead_channels:
            self.spike_time_plot_widget.plot(self.label_index, self.st_index)
            self.spike_sorting_plot_widget.plot(self.label, self.st_index)

    @QtCore.pyqtSlot(str)
    def on_channel_selection_changed(self, label):
        self.label = label
        self.label_index = ChannelUtility.get_ordered_index(self.label)
        self.raw_trace_plot_widget.plot(self.label)
        self.histogram_plot_widget.plot(self.label_index)
        if self.label_index not in self.sc_reader.dead_channels:
            self.spike_time_plot_widget.plot(self.label_index, self.st_index)
            self.spike_sorting_plot_widget.plot(self.label, self.st_index)

    def on_spiketime_index_changed(self, index):
        self.st_index = index
        self.raw_trace_plot_widget.on_scatter_plot_updated(self.label_index, self.st_index)
        self.spike_time_plot_widget.plot(self.label_index, self.st_index)
        self.spike_sorting_plot_widget.plot(self.label, self.st_index)

