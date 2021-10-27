from PyQt5 import QtCore, QtWidgets
import numpy as np
import matplotlib.gridspec as gridspec
import seaborn as sns

from plots.plot_widget import PlotWidget
from plot_manager import PlotManager
from frequency_bands_analysis.frequency_band_analysis_thread import FrequencyBandAnalysisThread


class FrequencyBandsTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_indices, grid_labels, settings):
        super().__init__(parent)
        self.reader = reader
        self.grid_indices = grid_indices
        self.grid_labels = grid_labels
        self.settings = settings

        self.mea_file_view = parent

        self.frequency_bands_matrix = None
        self.frequency_bands_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        operation_layout = QtWidgets.QVBoxLayout()
        operation_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far')
        operation_layout.addWidget(self.operation_label)
        self.progress_label = QtWidgets.QLabel(self)
        operation_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        operation_layout.addWidget(self.progress_bar)

        main_layout.addLayout(operation_layout)

        tool_button_layout = QtWidgets.QVBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save results...")
        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.save_button.setEnabled(False) # will be enabled after plotting
        tool_button_layout.addWidget(self.save_button)

        main_layout.addLayout(tool_button_layout)

        self.plot_widget = PlotWidget(self, 'Frequency Bands Histogram')
        self.plot_widget.toolbar.hide()
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)

    def initialize_frequency_bands_analysis(self):
        if self.frequency_bands_matrix is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('Calculating PSD')
            self.frequency_bands_thread = FrequencyBandAnalysisThread(self, self.reader, self.grid_indices,
                                                                      self.grid_labels)
            self.frequency_bands_thread.progress_made.connect(self.on_progress_made)
            self.frequency_bands_thread.operation_changed.connect(self.on_operation_changed)
            self.frequency_bands_thread.data_updated.connect(self.on_data_updated)
            self.frequency_bands_thread.finished.connect(self.on_frequency_bands_thread_finished)

            # clear previous results
            self.mea_file_view.results.clear_frequency_analysis_results()

            debug_mode = False
            if debug_mode:
                self.frequency_bands_thread.run()
            else:
                self.frequency_bands_thread.start()

    @QtCore.pyqtSlot(list)
    def on_data_updated(self, data):
        # find Paper reference for this
        def get_band_name(frequency):
            if self.settings.analysis_mode == 0:
                if 0 <= frequency <= 1:
                    return '< 1 Hz'
                if 2 <= frequency < 6:
                    return 'delta'
                elif 6 <= frequency < 11:
                    return 'theta'
                elif 11 <= frequency < 16:
                    return 'alpha'
                elif 21 <= frequency < 41:
                    return 'beta'
                elif 41 <= frequency < 101:
                    return 'gamma'
                else:
                    return None
            elif self.settings.analysis_mode == 1:
                if 40 <= frequency < 60:
                    return '50 Hz'
                elif 340 <= frequency < 360:
                    return '350 Hz'
                else:
                    return None

        label, frequencies, powers = data[0], data[1], data[2]
        if self.settings.analysis_mode == 0:
            band_names = '< 1 Hz', 'delta', 'theta', 'alpha', 'beta', 'gamma'
        elif self.settings.analysis_mode == 1:
            band_names = '50 Hz', '350 Hz'

        # ToDo: Check these lines, they might cause bugs since the variable names are stored several times
        band_amplitude_map = dict()
        for band_name in band_names:
            band_amplitude_map[band_name] = []
        for freq, power in zip(frequencies, powers):
            band_name = get_band_name(freq)
            if band_name:
                band_amplitude_map[band_name].append(power)
        band_sum_map = dict()
        for band_name in band_names:
            band_amplitudes = band_amplitude_map[band_name]
            if len(band_amplitudes) > 0:
                band_sum_map[band_name] = np.mean(band_amplitudes)
            else:
                band_sum_map[band_name] = 0
        self.mea_file_view.results.add_frequency_analysis_result(label, band_sum_map)

    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    # this function updates the progress bar
    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")

    def on_frequency_bands_thread_finished(self):
        self.progress_label.setText('Finished :)')
        self.frequency_bands_thread = None
        self.plot()

    def plot(self):
        self.plot_widget.toolbar.show()
        sns.set()
        # here it is figured out how many rows the final plot should have
        rows = int(np.ceil(np.sqrt(len(self.mea_file_view.results.frequency_analysis_results))))

        spec = gridspec.GridSpec(ncols=rows, nrows=rows, figure=self.figure, hspace=0.1, wspace=0.25)
        # iterate through all channels
        for idx, result in enumerate(sorted(self.mea_file_view.results.frequency_analysis_results,
                                            key=lambda r: r.label)):
            ax = self.figure.add_subplot(spec[idx])

            if self.settings.analysis_mode == 0:
                band_names = '< 1 Hz', 'delta', 'theta', 'alpha', 'beta', 'gamma'
            elif self.settings.analysis_mode == 1:
                band_names = '50 Hz', '350 Hz'
            means = []
            for band in result.band_map.keys():
                mean = result.band_map[band]
                means.append(mean)

            # calculate sum of amplitudes
            if self.settings.analysis_mode == 0:
                xticklabels = [r'$\leq$ 1 Hz', r'$\delta$', r'$\theta$', r'$\alpha$', r'$\beta$', r'$\gamma$']
            elif self.settings.analysis_mode == 1:
                xticklabels = ['50 Hz', '350 Hz']
            ax.bar(range(len(means)), means, align='center')
            ax.set_xticks(range(len(means)))
            ax.set_xticklabels(xticklabels)
            ax.set_ylim([0, 1.5])   # I hardcoded 1.5 since the highest amplitude usually is below that
        self.figure.text(0.5, 0.01, 'frequency bands', ha='center')
        self.figure.text(0.01, 0.5, r'mean power [$\mu V^{2}/$Hz]', va='center', rotation='vertical')
        PlotManager.instance.add_plot(self.plot_widget)
        # enable save button only after plotting
        self.save_button.setEnabled(True)

    def on_save_button_clicked(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setNameFilter("CSV files (*.csv)")
        file_dialog.setDefaultSuffix(".csv")
        file_dialog_result = file_dialog.exec()
        if file_dialog_result:
            # user selected file:
            selected_file = file_dialog.selectedFiles()[0]
            self.mea_file_view.results.save_frequency_analysis_results_to(selected_file)

    def is_busy_analyzing_frequencies(self):
        return self.frequency_bands_thread is not None

    def can_be_closed(self):
        # only allow closing if not busy
        return not self.is_busy_analyzing_frequencies()





