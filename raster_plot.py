from IPython import embed
import numpy as np


class RasterPlot:
    def __init__(self, figure, spike_mat):
        fig = figure
        spike_mat = spike_mat
        self.plot(fig, spike_mat)

    def plot(self, fig, spike_mat):
        ax = fig.add_subplot(111)
        # time = None
        # time_row_index = -1
        # yticklabels = [row[0] for row in spike_mat]
        # labels_fill = [(label[0] + str(0) + label[1], idx) if len(label) == 2 else (label, idx) for idx, label
        #                in enumerate(yticklabels)]
        # labels_sort = sorted(labels_fill, key=lambda label: label[0].lower())
        # indices = [item[1] for item in labels_sort]
        # time_row_index = [index for index, row in enumerate(spike_mat) if row[0].startswith('time')]
        # # embed()
        #
        # for i, idx in enumerate(indices):
        #     if idx != time_row_index[0]:
        #         print(spike_mat[idx][0] + ': \n')
        #         row = spike_mat[idx][1]
        #         print(row)
        #         if i % 2 == 0:
        #             color = 'k'
        #             yticklabels.append(spike_mat[idx][0])
        #         else:
        #             color = '#596163'
        for i in range(len(spike_mat)):
            if i % 2 == 0:
                color = 'k'
                # yticklabels.append(spike_mat[idx][0])
            else:
                color = '#596163'
            ax.scatter(spike_mat[i][1:], np.ones(len(spike_mat[i][1:])) * i, marker='|', color=color)

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.set_yticklabels(yticklabels)
        for label in ax.yaxis.get_ticklabels()[::2]:
            label.set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax.tick_params(labelsize=10, direction='out')