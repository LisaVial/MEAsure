from PyQt5 import QtCore, QtWidgets
import numpy as np

from plots.plot_settings import PlotSettings
from plot_manager import PlotManager
from plots.plot_creation_thread import PlotCreationThread
from plots.plot_widget import PlotWidget


class RasterplotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.colors = ['#749800', '#006d7c']

        self.spiketimes = self.reader.spiketimes
        self.plot_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        plot_name = 'Rasterplot_' + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):
        fs = 10000
        ax = fig.add_subplot(111)
        for i in range(len(spike_mat)):
            if i % 2 == 0:
                c = self.colors[0]
            else:
                c = self.colors[1]
            ax.scatter(spike_mat[i]/fs, np.ones(len(spike_mat[i])) * i, marker='|', color=c)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        labels = [item.get_text() for item in ax.get_yticklabels()]
        empty_string_labels = [''] * len(labels)
        ax.set_yticklabels(empty_string_labels)
        ax.set_ylabel('MEA channels')
        xlims = ax.get_xlim()
        ax.set_xticks([0, xlims[1]/2, xlims[1]])
        ax.set_xlim([0, xlims[1]])
        ax.set_xticklabels(['0', '150', '300'])
        ax.set_xlabel('time [s]')
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax.tick_params(labelsize=10, direction='out')
