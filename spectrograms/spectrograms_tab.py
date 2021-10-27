from PyQt5 import QtCore, QtWidgets
import seaborn as sns
import numpy as np
import matplotlib.cm
from IPython import embed

from plots.plot_widget import PlotWidget
# To Do: add plot manager to this tab
from plot_manager import PlotManager
from spectrograms.spectograms_thread import SpectrogramsThread


class SpectrogramsTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_indices, grid_labels, settings):
        super().__init__(parent)
        self.reader = reader
        self.grid_indices = grid_indices
        self.grid_labels = grid_labels
        self.settings = settings

        self.mea_file_view = parent

        self.spectograms_thread = None
        self.frequencies, self.time, self.Sxx = None, None, None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        operation_layout = QtWidgets.QVBoxLayout()
        operation_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

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

        self.plot_tab_widget = QtWidgets.QTabWidget(self)
        self.plot_tab_widget.setMovable(True)
        self.plot_tab_widget.setTabsClosable(False)
        self.plot_tab_widget.setUsesScrollButtons(True)
        main_layout.addWidget(self.plot_tab_widget)

    def initialize_spectrogram_calculation(self):
        if self.frequencies is None:
            filtered = self.mea_file_view.results.get_filter_mat()
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('Calculating spectrograms')
            self.spectograms_thread = SpectrogramsThread(self, self.reader, self.grid_indices, self.grid_labels,
                                                         filtered)
            self.spectograms_thread.progress_made.connect(self.on_progress_made)
            self.spectograms_thread.operation_changed.connect(self.on_operation_changed)
            self.spectograms_thread.finished.connect(self.on_spectrograms_thread_finished)

            debug_mode = False
            if debug_mode:
                self.spectograms_thread.run()
            else:
                self.spectograms_thread.start()

    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + '%')

    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.operation_label.setText(operation)

    def on_spectrograms_thread_finished(self):
        self.progress_label.setText('Finished :)')
        self.frequencies = self.spectograms_thread.frequencies
        self.time = self.spectograms_thread.time
        self.Sxx = self.spectograms_thread.Sxx
        self.spectograms_thread = None
        self.plot()

    def plot(self):
        for idx, label in enumerate(self.grid_labels):
            self.create_plot_tab(label)
            plot_widget = self.get_plot_widget(label)
            sns.set()
            fig = plot_widget.figure
            ax1 = fig.add_subplot(111)
            # overall_power = np.sum(self.Sxx[idx], axis=0)
            # embed()
            spec_values = 10 * np.log10(self.Sxx[idx]/np.max(self.Sxx[idx]))
            im = ax1.pcolormesh(self.time[idx], self.frequencies[idx], spec_values, shading='nearest', vmin=-60,
                                vmax=0)
            # ax1.plot(self.time[idx], overall_power)
            # ax1.set_ylim(0, 100)
            ax1.set_ylabel('frequency [Hz]')
            ax1.set_xlabel('time [sec]')
            cbar = fig.colorbar(im, ax=ax1)
            cbar.set_label('power [dB]')

    def create_plot_tab(self, label):
        plot_name = 'Spectogram_' + self.reader.filename + '_' + label
        plot_widget = PlotWidget(self, plot_name)
        self.plot_tab_widget.addTab(plot_widget, label)

    def get_plot_widget(self, label):
        found_tab_index = -1
        for tab_index in range(self.plot_tab_widget.count()):
            if self.plot_tab_widget.tabText(tab_index) == label:
                found_tab_index = tab_index
                break

        if found_tab_index >= 0:
            return self.plot_tab_widget.widget(found_tab_index)
        else:
            return None

    def can_be_closed(self):
        # only closeable if spike detection is not running currently
        return True
