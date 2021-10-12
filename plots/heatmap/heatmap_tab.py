from PyQt5 import QtCore, QtWidgets
import numpy as np
import seaborn as sns
from IPython import embed

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget
from utility.channel_utility import ChannelUtility


class HeatmapTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, mcs_channel_ids, settings):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.ch_ids = mcs_channel_ids
        self.colors = ['#749800', '#006d7c']
        self.single_heatmap = []

        self.spiketimes = self.reader.spiketimes
        # embed()

        self.plot_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        plot_name = 'Heatmap_' + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):
        fs = self.reader.sampling_frequency
        ax = fig.add_subplot(111)
        self.single_heatmap = []
        old_heatmap = self.settings.heatmap_for_normalizing
        for raw_index in self.ch_ids:
            # raw index simply corresponds to all channels (0 = A2, 1 = A3, ...) even if some are dead channels
            # if idx not in self.reader.dead_channels and
            # len(spike_mat[sc_channel_counter])/self.reader.duration >= 0.05:
            if self.reader.dead_channels:
                if raw_index not in self.reader.dead_channels:
                    sc_index = ChannelUtility.get_sc_index(raw_index, self.reader.dead_channels)
                    self.single_heatmap.append(len(spike_mat[sc_index]))
                else:
                    # raw index is pointing at dead channel
                    self.single_heatmap.append(0)
            else:
                # no dead channels -> raw index is sc channel index (all channels were recorded)
                self.single_heatmap.append(len(spike_mat[raw_index]))

        self.single_heatmap.insert(0, 0)
        self.single_heatmap.insert(15, 0)
        self.single_heatmap.insert(15 * 16, 0)
        self.single_heatmap.append(0)
        self.single_heatmap = np.reshape(self.single_heatmap, (16, 16)).transpose()
        # if old_heatmap is not None:
        #     self.single_heatmap = self.single_heatmap / np.array(old_heatmap)
        #     self.single_heatmap = np.nan_to_num(self.single_heatmap)
        y_labels = range(1, 17)
        x_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R']
        xticks = np.arange(0.5, 16.5, 1)
        if old_heatmap is not None:
            sns.heatmap(self.single_heatmap, cmap='hot_r', vmin=0, vmax=np.max(old_heatmap), ax=ax,
                         cbar_kws={'label': 'spike count'})
            # sns.heatmap(self.single_heatmap, cmap='PuBuGn', vmin=0, vmax=np.max(old_heatmap), ax=ax,
            #           cbar_kws={'label': 'spike count'})
        else:
            sns.heatmap(self.single_heatmap, cmap='hot_r', vmin=0, vmax=np.max(self.single_heatmap), ax=ax,
                        cbar_kws={'label': 'spike count'})
            # sns.heatmap(self.single_heatmap, cmap='PuBuGn', vmin=0, vmax=np.max(self.single_heatmap), ax=ax,
            #             cbar_kws={'label': 'spike count'})
        yticks = np.arange(0.5, 16.5, 1)
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        ax.set_yticklabels(y_labels)
        ax.set_xticklabels(x_labels)
        ax.set_ylabel('MEA rows')
        ax.set_xlabel('MEA columns')

        PlotManager.instance.add_plot(self.plot_widget)

    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
