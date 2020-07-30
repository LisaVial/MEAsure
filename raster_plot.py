from IPython import embed
import numpy as np
import matplotlib.cm as cm
import string


class RasterPlot:
    def __init__(self, figure, spike_mat):
        fig = figure
        spike_mat = spike_mat
        self.plot(fig, spike_mat)

    def plot(self, fig, spike_mat):
        ax = fig.add_subplot(111)
        yticklabels = []

        for i in range(len(spike_mat)):
            if len(spike_mat[i]) < 2:
                continue
            if i % 4 == 0:
                label = ''.join(spike_mat[i])
                yticklabels.append(label)
            if i % 3 == 2:
                ax.scatter(spike_mat[i], np.ones(len(spike_mat[i])) * i/4, marker='|', c=np.arange(len(spike_mat[i])),
                           cmap="PuBuGn")
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ytick_range = range((int(len(spike_mat)/4)))
        ax.set_yticks(ytick_range)
        labels = [item.get_text() for item in ax.get_yticklabels()]
        empty_string_labels = [''] * len(labels)
        for idx in range(len(empty_string_labels)):
            if idx % 12 == 0:
                empty_string_labels[idx] = empty_string_labels[idx].replace('', yticklabels[idx])
        ax.set_yticklabels(yticklabels)
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