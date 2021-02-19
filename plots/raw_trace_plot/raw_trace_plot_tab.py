from PyQt5 import QtCore, QtWidgets
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class RawTracePlotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, settings, grid_labels, grid_indices):
        super().__init__(parent)
        self.reader = reader
        self.settings = settings
        self.grid_labels = grid_labels
        self.grid_indices = grid_indices

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        plot_name = 'Raw_trace_channel_' + str(self.grid_label) + self.reader.filename

        self.plot_tab_widget = QtWidgets.QTabWidget(self)
        self.plot_tab_widget.setMovable(True)
        self.plot_tab_widget.setTabsClosable(False)
        self.plot_tab_widget.setUsesScrollButtons(True)
        main_layout.addWidget(self.plot_tab_widget)
        self.plot()

    def plot(self):
        for idx, label in enumerate(self.grid_labels):
            self.create_plot_tab(label)
            plot_widget = self.get_plot_widget(label)
            sns.set()
            fig = plot_widget.figure
            ax = fig.add_subplot(111)
            ax.plot()


    def create_plot_tab(self, label):
        plot_name = 'Raw_trace_' + self.reader.filename + '_' + label
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