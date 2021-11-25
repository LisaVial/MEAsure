from PyQt5 import QtCore, QtWidgets
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class RawTracePlotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings, grid_labels, grid_indices, sampling_rate):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.grid_labels = grid_labels
        self.grid_indices = grid_indices
        self.fs = sampling_rate

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        self.plot_tab_widget = QtWidgets.QTabWidget(self)
        self.plot_tab_widget.setMovable(True)
        self.plot_tab_widget.setTabsClosable(False)
        self.plot_tab_widget.setUsesScrollButtons(True)
        main_layout.addWidget(self.plot_tab_widget)
        self.plot()

    def plot(self):
        for idx, label in enumerate(self.grid_labels):

            ## test
            if label in self.settings.channel_time_selection.keys():
                start_index, end_index = self.settings.channel_time_selection[label]
                start_time = int(start_index)
                end_time = int(end_index)
            else:
                start_time = int(self.settings.start_time)
                end_time = int(self.settings.end_time)
            #######

            print('raw trace plot:', label, '->', idx)
            self.create_plot_tab(label)
            plot_widget = self.get_plot_widget(label)
            sns.set()
            fig = plot_widget.figure
            ax = fig.add_subplot(111)

            plot_time = np.arange(start_time, end_time, 1/self.fs)
            scaled_trace = self.reader.get_scaled_channel(label)
            ax.plot(plot_time, scaled_trace[int(start_time*self.fs):int(end_time*self.fs)])
            ax.set_xlim([plot_time[0], plot_time[-1]])
            ax.set_ylabel(r'amplitude [$\mu$ V]')
            ax.set_xlabel(r'time [s]')

            PlotManager.instance.add_plot(plot_widget)

    def create_plot_tab(self, label):
        plot_name = 'Raw_trace_channel_' + str(label) + '_' + self.reader.filename
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
        # plot is not running a thread => can be always closed
        return True