from PyQt5 import QtCore, QtWidgets
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import seaborn as sns
from IPython import embed

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

        self.plot_tab_widget = QtWidgets.QTabWidget(self)
        self.plot_tab_widget.setMovable(True)
        self.plot_tab_widget.setTabsClosable(False)
        self.plot_tab_widget.setUsesScrollButtons(True)
        main_layout.addWidget(self.plot_tab_widget)

    def initialize_frequency_bands_analysis(self):
        if self.frequency_bands_matrix is None:
            filtered = self.mea_file_view.results.get_filter_mat()
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('Calculating PSD')
            self.frequency_bands_thread = FrequencyBandAnalysisThread(self, self.reader, self.grid_indices,
                                                                      self.grid_labels, filtered)
            self.frequency_bands_thread.progress_made.connect(self.on_progress_made)
            self.frequency_bands_thread.operation_changed.connect(self.on_operation_changed)
            self.frequency_bands_thread.data_updated.connect(self.on_data_updated)
            self.frequency_bands_thread.finished.connect(self.on_frequency_bands_thread_finished)

            debug_mode = False
            if debug_mode:
                self.frequency_bands_thread.run()
            else:
                self.frequency_bands_thread.start()

    @QtCore.pyqtSlot(list)
    def on_data_updated(self, data):
        # utility functions
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
        sns.set()
        for plot_idx, plot_type_str in enumerate(['Histogram', 'Row comparison']):
            if plot_idx == 0:
                self.create_plot_tab(plot_type_str)
                plot_widget = self.get_plot_widget(plot_type_str)
                sns.set()
                fig = plot_widget.figure
                rows = int(np.ceil(np.sqrt(len(self.mea_file_view.results.frequency_analysis_results))))

                spec = gridspec.GridSpec(ncols=rows, nrows=rows, figure=fig, hspace=0.1, wspace=0.25)

                # iterate through all channels
                for idx, result in enumerate(sorted(self.mea_file_view.results.frequency_analysis_results,
                                                    key=lambda r: r.label)):
                    ax = fig.add_subplot(spec[idx])

                    if self.settings.analysis_mode == 0:
                        band_names = '< 1 Hz', 'delta', 'theta', 'alpha', 'beta', 'gamma'
                    elif self.settings.analysis_mode == 1:
                        band_names = '50 Hz', '350 Hz'
                    means = []
                    for band in band_names:
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
                    # ax.set_ylim(0, max)

                # embed()
                fig.text(0.5, 0.01, 'frequency bands', ha='center')
                fig.text(0.01, 0.5, r'mean power [$\mu V^{2}/$Hz]', va='center', rotation='vertical')
                fig.tight_layout(h_pad=0.2, w_pad=0.4)
                PlotManager.instance.add_plot(plot_widget)
                # enable save button only after plotting
                self.save_button.setEnabled(True)

            elif plot_idx == 1:
                self.create_plot_tab(plot_type_str)
                plot_widget = self.get_plot_widget(plot_type_str)
                sns.set()
                fig = plot_widget.figure
                key_ints = range(round(len(self.grid_labels) / 16))
                rows = int(round(len(self.grid_labels) / 16))
                spec = gridspec.GridSpec(ncols=1, nrows=rows, figure=fig, hspace=0.9)

                rows = dict()

                if self.settings.analysis_mode == 0:
                    band_names = '< 1 Hz', 'delta', 'theta', 'alpha', 'beta', 'gamma'
                    xticklabels = [r'$\leq$ 1 Hz', r'$\delta$', r'$\theta$', r'$\alpha$', 'SMR', r'$\beta$',
                                   r'$\gamma$']
                elif self.settings.analysis_mode == 1:
                    band_names = '50 Hz', '350 Hz'
                    xticklabels = ['50 Hz', '350 Hz']
                for key_int in key_ints:
                    rows[key_int] = dict()
                    for band in band_names:
                        rows[key_int][band] = []
                x_labels = []
                maxs = []
                for idx, result in enumerate(sorted(self.mea_file_view.results.frequency_analysis_results,
                                                    key=lambda r: r.label)):
                    x_labels.append(result.label)
                    # reorganize dictionary that saves plot information
                    row_index = int(result.label[1:]) - 1 # -1 to map first row to index 0
                    for key in list(result.band_map.keys()):
                        rows[row_index][key].append(result.band_map[key])
                for key_idx, key in enumerate(list(rows.keys())):
                    ax = fig.add_subplot(spec[key_idx])
                    for j, band_key in enumerate(list(rows[key_idx].keys())):
                        if key_idx == 0:
                            # the next three code lines are to fake an x-offset in the beginning and the end of the plot
                            # of the first row since there are no channels A1 and R1
                            values = np.zeros(1)
                            values = np.append(values, rows[key_idx][band_key])
                            values = np.append(values, 0)

                            ax.plot(np.arange(1, len(rows[key_idx][band_key]) + 3), values,
                                    label=band_key, alpha=0.5)
                            ax.fill_between(np.arange(1, len(rows[key_idx][band_key]) + 3),
                                            np.zeros(len(values)), values,
                                            alpha=0.5)
                            xlabels = ['', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'J1', 'K1', 'L1', 'M1', 'N1', 'O1',
                                       'P1', '']
                            ax.set_xticks(np.arange(1, len(rows[key_idx][band_key])+3))
                            ax.set_xticklabels(xlabels)
                        else:
                            ax.plot(np.arange(1, len(rows[key_idx][band_key]) + 1), rows[key_idx][band_key], alpha=0.5)
                            ax.fill_between(np.arange(1, len(rows[key_idx][band_key]) + 1),
                                            np.zeros(len(rows[key_idx][band_key])), rows[key_idx][band_key], alpha=0.5)
                            xlabels = [letter + str(key_idx+1) for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                                                                              'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R']]
                            ax.set_xticks(np.arange(1, len(rows[key_idx][band_key]) + 1))
                            ax.set_xticklabels(xlabels)
                        maxs.append(np.max(rows[key_idx][band_key]))
                axs = fig.get_axes()
                for axi in axs:
                    axi.set_ylim(0, np.max(maxs)+5)
                fig.text(0.5, 0.01, 'channel', ha='center')
                fig.text(0.01, 0.5, r'mean power [$\mu V^{2}/$Hz]', va='center', rotation='vertical')
                fig.legend()
                # fig.tight_layout(h_pad=0.2, w_pad=0.4)

                # embed()
                # print(rows)

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

    def create_plot_tab(self, plot_type_str):
        plot_name = plot_type_str + self.reader.filename
        plot_widget = PlotWidget(self, plot_name)
        self.plot_tab_widget.addTab(plot_widget, plot_type_str)

    def get_plot_widget(self, plot_type_str):
        found_tab_index = -1
        for tab_index in range(self.plot_tab_widget.count()):
            if self.plot_tab_widget.tabText(tab_index) == plot_type_str:
                found_tab_index = tab_index
                break

        if found_tab_index >= 0:
            return self.plot_tab_widget.widget(found_tab_index)
        else:
            return None





