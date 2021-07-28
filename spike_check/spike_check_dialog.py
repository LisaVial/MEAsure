import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from spike_check.channel_selection_widget import ChannelSelectionWidget
from spike_check.raw_trace_w_threshold_plot import RawTraceWThresholdPlot
from spike_check.voltage_trace_histogram_plot import VoltageTraceHistogramPlot
from spike_check.spike_time_plot import SpikeTimePlot
from spike_check.navigation_buttons_widget import NavigationButtonsWidget
from spike_check.preprocessing_thread import PreprocessingThread
from spike_check.spike_sorting_plot import SpikeSortingPlot

from utility.channel_utility import ChannelUtility
from utility.worker_thread import WorkerThread


class SpikeCheckDialog(QtWidgets.QDialog):
    def __init__(self, parent, mcs_reader, sc_reader):
        super().__init__(parent)

        self.mcs_reader = mcs_reader
        self.sc_reader = sc_reader
        self.st_index = 0

        self.pre_proc_thread = None
        self.filtered_matrix = None
        self.preproc_mat = None

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
        main_layout.addWidget(self.raw_trace_plot_widget, 1, 0, 1, 2)

        # insert a plot widget which shows 10 ms around a spike (it would be great if the spiketime is also indicated in
        #   the first plot widget)
        self.spike_time_plot_widget = SpikeTimePlot(self, self.mcs_reader, self.sc_reader, self.label, self.label_index)
        main_layout.addWidget(self.spike_time_plot_widget, 2, 0)

        self.spike_sorting_plot_widget = SpikeSortingPlot(self, self.mcs_reader, self.sc_reader, self.label)
        main_layout.addWidget(self.spike_sorting_plot_widget, 2, 1)

        # buttons on the bottom of the dialog to navigate through spike times
        max_idx = len(self.sc_reader.spiketimes[self.label_index]) - 1
        self.navigation_buttons_widget = NavigationButtonsWidget(self, max_idx)
        main_layout.addWidget(self.navigation_buttons_widget, 3, 0, 1, 2)
        self.navigation_buttons_widget.index_changed.connect(self.on_spiketime_index_changed)

        # self.histogram_plot_widget.plot(self.label_index)
        self.spike_time_plot_widget.plot(self.label_index, self.st_index)
        self.raw_trace_plot_widget.plot(self.label)
        self.spike_sorting_plot_widget.plot(self.label, self.st_index)

        self.worker = WorkerThread(self)
        self.worker_thread.finished.connect(self.on_worker_thread_finished)

    @QtCore.pyqtSlot()
    def on_worker_thread_finished(self):
        QtWidgets.QApplication.instance().main_window.animation_overlay.stop()

    @QtCore.pyqtSlot()
    def initialize_preprocessing_thread(self):
        if self.preproc_mat is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.pre_proc_thread = PreprocessingThread(self, self.mcs_reader, self.sc_reader)
            self.pre_proc_thread.progress_made.connect(self.on_progress_made)
            self.pre_proc_thread.operation_changed.connect(self.on_operation_changed)
            self.pre_proc_thread.finished.connect(self.on_pre_proc_thread_finished)

            debug_mode = True  # set to 'True' in order to debug plot creation with embed
            if debug_mode:
                # synchronous plotting (runs in main thread and thus allows debugging)
                self.pre_proc_thread.run()
            else:
                # asynchronous plotting (default):
                self.pre_proc_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately

    # this function changes the label of the progress bar to inform the user what happens in the backgound
    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    # this function updates the progress bar
    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")

    @QtCore.pyqtSlot()
    def on_pre_proc_thread_finished(self):
        self.progress_label.setText("Finished :)")
        if self.pre_proc_thread.preproc_matrix is not None:
            self.preproc_mat = self.pre_proc_thread.preproc_matrix.copy()
        if self.pre_proc_thread.filtered_matrix is not None:
            self.filtered_matrix = self.pre_proc_thread.filtered_matrix.copy()

        self.pre_proc_thread = None
        self.raw_trace_plot_widget.plot(self.label, self.preproc_mat)

    @QtCore.pyqtSlot(str)
    def on_channel_selection_changed(self, label):
        self.label = label
        self.label_index = ChannelUtility.get_ordered_index(self.label)
        # if self.preproc_mat is not None:
        # self.histogram_plot_widget.plot(self.label_index)
        self.spike_time_plot_widget.plot(self.label_index, self.st_index)
        self.raw_trace_plot_widget.plot(self.label)
        self.spike_sorting_plot_widget.plot(self.label, self.st_index)

    def on_spiketime_index_changed(self, index):
        self.st_index = index
        self.raw_trace_plot_widget.on_scatter_plot_updated(self.label_index, self.st_index)
        self.spike_time_plot_widget.plot(self.label_index, self.st_index)
        self.spike_sorting_plot_widget.plot(self.label, self.st_index)

