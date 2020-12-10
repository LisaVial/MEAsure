from PyQt5 import QtWidgets, QtCore
import numpy as np
from scipy.signal import filtfilt, butter, find_peaks, peak_prominences
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from plot_manager import PlotManager
from plots.plot_widget import PlotWidget


class CsdPlotTab(QtWidgets.QWidget):
    def __init__(self, parent, reader, grid_channel_indices, grid_labels, fs, settings):
        # sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
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

        self.ch_ids = self.reader.channel_ids
        self.labels = self.reader.labels
        self.fs = self.reader.sampling_frequency
        self.duration = self.reader.current_file['duration']

        self.plot(self.figure)

    def plot(self, figure):
        time = np.arange(0, self.reader.voltage_traces_dataset.shape[1]/self.fs, 1/self.fs)

        big_proms = []
        channel_order = []
        filtered = []
        for idx, label in enumerate(self.grid_labels):
            signal = self.reader.get_traces_with_label(label)
            fs = self.reader.sampling_frequency

            nyq = 0.5 * fs
            normal_cutoff = 10 / nyq
            b, a = butter(2, normal_cutoff, btype='low', analog=False)
            y = filtfilt(b, a, signal)

            peaks, _ = find_peaks(y, threshold=np.mean(y))
            print(peaks)
            proms = peak_prominences(y, peaks)[0]
            labels = []
            if 200 < proms[0] < 500:
                for char in str(self.grid_labels[idx]):
                    print(ord(char))
                    # ord(char) method to check for char elements by their ascii value
                    # checking for char elements with upper case
                    if 65 <= ord(char) <= 90:
                        labels.append(char)
                    # checking for char elements with lower case
                    elif 97 <= ord(char) <= 122:
                        labels.append(char)
                filtered.append(y[10000:100001])
                big_proms.append(proms[0])
                channel_order.append(idx)

        print(labels)
        df = pd.DataFrame(dict(x=filtered, g=labels))
        m = df.g.map(ord)
        df["x"] += m

        pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
        g = sns.FacetGrid(df, row="g", hue="g", aspect=15, height=.5, palette=pal)

        g.map(sns.lineplot, data='x', clip_on=False, fill=True, alpha=1, linewidth=1.5)
        g.map(plt.axhline, y=0, lw=2, clip_on=False)

        # Define and use a simple function to label the plot in axes coordinates
        def label(x, color, label):
            ax = plt.gca()
            ax.text(0, .2, label, fontweight="bold", color=color,
                    ha="left", va="center", transform=ax.transAxes)

        g.map(label, "x")

        # Set the subplots to overlap
        g.fig.subplots_adjust(hspace=-.25)

        # Remove axes details that don't play well with overlap
        g.set_titles("")
        g.set(yticks=[])
        g.despine(bottom=True, left=True)


    def can_be_closed(self):
        # plot is not running a thread => can be always closed
        return True
