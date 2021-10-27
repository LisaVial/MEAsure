from PyQt5 import QtCore, QtWidgets
import numpy as np
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget
from utility import channel_utility


class RasterplotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings, sampling_rate, duration, grid_labels, grid_indices):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.fs = sampling_rate
        self.duration = duration
        self.grid_labels = grid_labels
        self.grid_indices = grid_indices

        self.mea_file_view = parent

        self.colors = ['#749800', '#006d7c']
        self.dead_channels = []
        if 'SC' in str(self.reader):
            self.dead_channels = self.reader.dead_channels

        # i will not need a dictionary, except if that is better for saving in .csv files
        spiketimes_len = len(self.grid_indices)
        max_spike_count = max([len(self.reader.spiketimes[i]) for i in range(len(self.reader.spiketimes))])
        self.spiketimes = np.full([spiketimes_len, max_spike_count], np.nan)
        for idx, mcs_index in enumerate(self.grid_indices):
            if mcs_index in self.dead_channels:
                # self.spiketimes.append(np.array([]))
                # spiketimes matrix already consists of empy channels, so continue
                self.mea_file_view.results.get_spiketimes_from_rasterplot(self.grid_labels[idx],
                                                                          self.spiketimes[idx]
                                                                          [~np.isnan(self.spiketimes[idx])] / self.fs)
                continue
            else:
                sc_index = channel_utility.ChannelUtility.get_sc_index(mcs_index, self.dead_channels)
                spiketimes_count = len(self.reader.spiketimes[sc_index])
                self.spiketimes[idx, :spiketimes_count] = np.array(self.reader.spiketimes[sc_index])
            self.mea_file_view.results.get_spiketimes_from_rasterplot(self.grid_labels[idx],
                                                                      self.spiketimes[idx]
                                                                      [~np.isnan(self.spiketimes[idx])]/self.fs)

        print(self.spiketimes)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        tool_button_layout = QtWidgets.QVBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save results...")
        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.save_button.setEnabled(False)  # will be enabled after plotting
        tool_button_layout.addWidget(self.save_button)
        main_layout.addLayout(tool_button_layout)

        plot_name = 'Rasterplot_' + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

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
            self.mea_file_view.results.save_rasterplot_data_to(selected_file)

    def plot(self, fig, spike_mat):
        # determine how many grid labels to skip for the labels of the y-axis
        label_step_size = max(1, int(np.ceil(len(spike_mat) / 16.0)))

        sns.set()
        fs = self.fs
        ax = fig.add_subplot(111)
        # spike_mat.reverse()
        sts = [spike_mat[i][~np.isnan(spike_mat[i])] for i in range(len(spike_mat))]
        sts = np.flip(sts)
        print(type(sts))
        ax.eventplot(np.array(sts)/fs)
        if len(self.grid_labels) == 1:
            ax.set_yticks([1.0])
            ax.set_yticklabels([self.grid_labels[0]])
        else:
            ax.set_yticks(np.arange(0, len(self.grid_labels), label_step_size))
            ax.set_yticklabels(self.grid_labels[(len(self.grid_labels) -1)::-label_step_size])
        ax.set_ylabel('MEA channels')
        ax.set_xlabel('time [s]')
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax.tick_params(labelsize=10, direction='out')
        PlotManager.instance.add_plot(self.plot_widget)
        self.save_button.setEnabled(True)

    # can this be static?
    @staticmethod
    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
