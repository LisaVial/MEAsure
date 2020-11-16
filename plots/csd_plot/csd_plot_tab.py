from PyQt5 import QtWidgets, QtCore
import numpy as np
import os
import matplotlib as plt


from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class CsdPlotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_channel_indices, duration, settings):
        super().__init__(parent)
        self.reader = reader
        self.grid_channel_indices = grid_channel_indices
        self.duration = duration
        self.settings = settings

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        file_name = os.path.split(self.reader.file_path)[1]
        plot_name = 'CSD_Plot_' + file_name

        self.plot_widget = PlotWidget(self, plot_name)
        self.figure = self.plot_widget.figure
        main_layout.addWidget(self.plot_widget)

        self.signal = self.reader.voltage_traces[:]
        self.ch_ids = self.reader.channel_indices
        self.labels = self.reader.labels
        self.fs = self.reader.sampling_frequency

        self.plot(self.figure)

    def plot(self, figure):
        time = np.arange(0, self.duration + 1/self.fs, 1/self.fs)
        color_count = 8
        colors = [plt.cm.Pastel2(x) for x in np.linspace(0.0, 1.0, color_count)]

        selected_ids = [self.ch_ids[g_idx] for g_idx in self.grid_channel_indices]

        ax = figure.add_subplot(111)
        if self.ch_ids is not None:
            for idx, ch_id in enumerate(reversed(selected_ids)):
                if len(self.labels[idx]) < 3:
                    ax.plot(time, self.signal[ch_id] + idx*10000, color=colors[idx % color_count], lw=4)

            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
        else:
            for idx in range(len(self.signal)):
                ax.plot(time, self.signal[idx]-1 + idx*10000, color=colors[idx % color_count], lw=4)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
        labels = self.reader.labels
        label_locs = [item.get_text() for item in ax.get_yticklabels()]
        empty_string_labels = [''] * len(label_locs)
        for idx in range(len(empty_string_labels)):
            if idx % 12 == 0:
                empty_string_labels[idx] = empty_string_labels[idx].replace('', labels[ch_id])
        ax.set_yticklabels(empty_string_labels)
        ax.set_xlabel('time')
        ax.set_ylabel('MEA channels')

    # @QtCore.pyqtSlot(int)
    # def on_tab_close_requested(self, index):
    #     # only close and remove tab if not currently loading/plotting
    #     plot_widget = self.widget(index)
    #     if not plot_widget.is_busy_plotting():
    #         plot_widget.close()
    #         self.removeTab(index)
