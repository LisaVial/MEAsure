import numpy as np


class RasterPlot:
    def __init__(self, figure, spike_mat):
        fig = figure
        spike_mat = spike_mat
        self.plot(fig, spike_mat)

    def plot(self, fig, spike_mat):
        ax = fig.add_subplot(111)
        time = None
        time_row_index = -1
        yticklabels = []
        for index, row in enumerate(spike_mat):
            if row[0].startswith('time'):
                time_row_index = index

        for i in range(len(spike_mat)):
            if i != time_row_index:
                yticklabels.append(spike_mat[i][0])
                row = spike_mat[i][1]
                if i%2 == 0:
                    color = 'k'
                else:
                    color = '#596163'
                ax.scatter(row, np.ones(len(row))*i, marker='|', color=color)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax.tick_params(labelsize=10, direction='out')