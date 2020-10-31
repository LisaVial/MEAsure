import numpy as np
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation


class LivePlotter:
    def __init__(self, figure, signal, threshold, spiketimes):
        self.figure = figure
        self.signal = signal
        self.threshold = threshold
        self.current_spikes = spiketimes
        FuncAnimation(self.figure, self.live_plot_signal_and_threshold, 500)
        plt.show()

    def live_plot_signal_and_threshold(self):
        spike_height = np.min(self.signal) - 1
        ax = self.figure.add_subplot(111)
        ax.plot(self.signal, color='#006E7D', label='recording')
        ax.plot(self.threshold, color='#D0797A', label='threshold')
        ax.scatter(self.current_spikes, np.ones(len(self.current_spikes))*spike_height, color='#A7C9BA',
                   label='spiketimes')
        plt.legend()
        plt.tight_layout()
