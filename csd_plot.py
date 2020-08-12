import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib as mpl
from IPython import embed


def multiline(xs, ys, c, ax, **kwargs):
    """Plot lines with different colorings

    Parameters
    ----------
    xs : iterable container of x coordinates
    ys : iterable container of y coordinates
    c : iterable container of numbers mapped to colormap
    ax (optional): Axes to plot on.
    kwargs (optional): passed to LineCollection

    Notes:
        len(xs) == len(ys) == len(c) is the number of line segments
        len(xs[i]) == len(ys[i]) is the number of points for each line (indexed by i)

    Returns
    -------
    lc : LineCollection instance.
    """
    # create LineCollection
    segments = [np.column_stack([x, y]) for x, y in zip(xs[0], ys[0])]
    lc = LineCollection(segments, **kwargs)

    # set coloring of line segments
    #    Note: I get an error if I pass c as a list here... not sure why.
    lc.set_array(np.asarray(c))

    # add lines to axes and rescale
    #    Note: adding a collection doesn't autoscalee xlim/ylim
    ax.add_collection(lc)
    ax.autoscale()
    return lc


class CsdPlot:
    def __init__(self, figure, reader):
        self.reader = reader
        signal = self.reader.voltage_traces[:]
        ch_ids = self.reader.channel_indices
        labels = self.reader.labels
        fs = self.reader.sampling_frequency
        self.plot(figure, signal, ch_ids, labels, fs)

    def plot(self, figure, signal, ch_ids, labels, fs):
        time = np.arange(0, len(signal[0])/fs, 1/fs)
        color_count = 8
        colors = [plt.cm.Pastel2(x) for x in np.linspace(0.0, 1.0, color_count)]

        ax = figure.add_subplot(111)
        for idx, ch_id in enumerate(reversed(ch_ids)):
            ax.plot(time[::1250], signal[ch_id][::1250]+(idx*1000), color=colors[idx % color_count], lw=4)

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # label_locs = [item.get_text() for item in ax.get_yticklabels()]
        # empty_string_labels = [''] * len(label_locs)
        # for idx in range(len(empty_string_labels)):
        #     if idx % 12 == 0:
        #         empty_string_labels[idx] = empty_string_labels[idx].replace('', labels[idx])
        # ax.set_yticklabels(empty_string_labels)
        # ax.set_xlabel('time')
        # ax.set_ylabel('MEA channels')
        # axcb = figure.colorbar(lc)
        # axcb.set_label('MEA channels')
        # plt.savefig('test.png')