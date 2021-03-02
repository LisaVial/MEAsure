import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from spike_check.channel_selection_widget import ChannelSelectionWidget
from spike_check.raw_trace_w_threshold_plot import RawTraceWThresholdPlot
from spike_check.voltage_trace_histogram_plot import VoltageTraceHistogramPlot
from spike_check.spike_time_plot import SpikeTimePlot
from spike_check.navigation_buttons_widget import NavigationButtonsWidget


class SpikeCheckDialog(QtWidgets.QDialog):
    def __init__(self, parent, mcs_reader, sc_reader):
        super().__init__(parent)

        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)

        self.setWindowTitle("Check detection of spiketimes")

        main_layout = QtWidgets.QGridLayout(self)
        # main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        # insert widget to select channel for which spikes should be checked
        channel_selection_widget = ChannelSelectionWidget(self)
        channel_selection_widget.channel_selection_changed.connect(self.on_channel_selection_changed)
        main_layout.addWidget(channel_selection_widget, 0, 0, 1, 2)
        self.label = channel_selection_widget.label
        self.index = channel_selection_widget.channel_selection_combobox.currentIndex()

        # insert plot widget that shows raw trace of channel: Plot title should show channel label, plot should show
        #   raw trace and thresholds (maybe get settings)
        self.raw_trace_plot_widget = RawTraceWThresholdPlot(self, self.mcs_reader, self.label)
        main_layout.addWidget(self.raw_trace_plot_widget, 1, 0)

        # insert plot widget that shows histogram of voltage trace values -> gaussian curve with tails hints to the
        #   channel having spikes
        self.histogram_plot_widget = VoltageTraceHistogramPlot(self, self.mcs_reader, self.label)
        main_layout.addWidget(self.histogram_plot_widget, 1, 1)

        # insert a plot widget which shows 10 ms around a spike (it would be great if the spiketime is also indicated in
        #   the first plot widget)
        self.spike_time_plot_widget = SpikeTimePlot(self, self.mcs_reader, self.sc_reader, self.label, self.index)
        main_layout.addWidget(self.spike_time_plot_widget, 2, 0, 1, 2)

        # buttons on the bottom of the dialog to navigate through spike times
        max_idx = len(self.sc_reader.spiketimes[self.index])
        self.navigation_buttons_widget = NavigationButtonsWidget(self, max_idx)
        main_layout.addWidget(self.navigation_buttons_widget, 3, 0, 1, 2)

    @QtCore.pyqtSlot(str)
    def on_channel_selection_changed(self, label, index):
        self.label = label
        self.index = index
        self.raw_trace_plot_widget.plot(self.label)
        self.histogram_plot_widget.plot(self.label)

