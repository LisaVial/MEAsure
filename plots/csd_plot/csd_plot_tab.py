from PyQt5 import QtWidgets, QtCore
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from IPython import embed

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class CsdPlotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_channel_indices, grid_labels, fs, settings):
        sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
        super().__init__(parent)
        self.reader = reader
        self.grid_channel_indices = grid_channel_indices
        self.grid_labels = grid_labels
        self.fs = fs
        self.settings = settings

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        file_name = self.reader.filename
        plot_name = 'CSD_Plot_' + file_name

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)

        self.signal = self.reader.voltage_traces[:]
        self.ch_ids = self.reader.channel_indices
        self.labels = self.reader.labels
        self.fs = self.reader.sampling_frequency

        # voltage_traces = [list(self.reader.voltage_traces[g_idx]) for g_idx in grid_channel_indices]
        # channel_labels =[self.reader.labels[g_idx] for g_idx in grid_channel_indices]
        # # time = np.arange(0, len(voltage_traces[0]) * (1/self.fs), 1/self.fs)
        # # time = np.repeat(time, len(voltage_traces))
        # # time = np.reshape(time, np.asarray(voltage_traces).shape)
        # self.df = pd.DataFrame(dict(x=voltage_traces, g=channel_labels))
        # pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
        # self.g = sns.FacetGrid(self.df, row="g", hue="g", aspect=15, height=.5, palette=pal)
        # # embed()
        self.plot(self.figure)

    def plot(self, figure):
        # self.g.map(sns.lineplot(self.df['x']))
        # # self.g.map(sns.kdeplot, self.df['x'])
        # self.g.map(plt.axhline, y=0, lw=2, clip_on=False)
        #
        # def label(x, color, label):
        #     ax = plt.gca()
        #     ax.text(0, .2, label, fontweight="bold", color=color, ha="left", va="center", transform=ax.transAxes)
        #
        # self.g.map(label, "x")
        #
        # # Set the subplots to overlap
        # self.g.fig.subplots_adjust(hspace=-.25)
        #
        # # Remove axes details that don't play well with overlap
        # self.g.set_titles("")
        # self.g.set(yticks=[])
        # self.g.despine(bottom=True, left=True)

        time = np.arange(0, self.duration + 1/self.fs, 1/self.fs)
        color_count = 8
        colors = [plt.cm.Pastel2(x) for x in np.linspace(0.0, 1.0, color_count)]

        # selected_ids = [self.ch_ids[g_idx] for g_idx in self.grid_channel_indices]

        # ax = figure.add_subplot(111)
        # if self.ch_ids is not None:
        #     for idx, ch_id in enumerate(reversed(selected_ids)):
        #         if len(self.labels[idx]) < 3:
        #             ax.plot(time, self.signal[ch_id] + idx*10000, color=colors[idx % color_count], lw=4)
        #
        #     ax.spines['right'].set_visible(False)
        #     ax.spines['top'].set_visible(False)
        # else:
        #     for idx in range(len(self.signal)):
        #         ax.plot(time, self.signal[idx]-1 + idx*10000, color=colors[idx % color_count], lw=4)
        #     ax.spines['right'].set_visible(False)
        #     ax.spines['top'].set_visible(False)
        # labels = self.reader.labels
        # label_locs = [item.get_text() for item in ax.get_yticklabels()]
        # empty_string_labels = [''] * len(label_locs)
        # for idx in range(len(empty_string_labels)):
        #     if idx % 12 == 0:
        #         empty_string_labels[idx] = empty_string_labels[idx].replace('', labels[ch_id])
        # ax.set_yticklabels(empty_string_labels)
        # ax.set_xlabel('time')
        # ax.set_ylabel('MEA channels')

    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
