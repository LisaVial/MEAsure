from PyQt5 import QtCore, QtWidgets
import numpy as np
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class HeatmapTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.colors = ['#749800', '#006d7c']

        self.spiketimes = self.reader.spiketimes
        self.plot_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        plot_name = 'Heatmap_' + self.reader.filename

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)
        self.plot(self.figure, self.spiketimes)

    def plot(self, fig, spike_mat):
        fs = 10000
        ax = fig.add_subplot(111)
        single_heatmap = []
        for spikes in spike_mat:
            try:
                single_heatmap.append(len(spikes))
            except:
                single_heatmap.append(0)
        single_heatmap.insert(0, 0)
        single_heatmap.insert(15, 0)
        single_heatmap.insert(15 * 16, 0)
        single_heatmap.append(0)
        single_heatmap = np.reshape(single_heatmap, (16, 16))
        y_labels = range(1, 17)
        x_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R']
        xticks = np.arange(0.5, 16.5, 1)
        sns.heatmap(single_heatmap, cmap='PuBuGn', vmin=0.1, vmax=np.max(single_heatmap), ax=ax)
        yticks = np.arange(0.5, 16.5, 1)
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        ax.set_yticklabels(y_labels)
        ax.set_xticklabels(x_labels)
        ax.set_ylabel('MEA rows')

        PlotManager.instance.add_plot(self.plot_widget)

    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
