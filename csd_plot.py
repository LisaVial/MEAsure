import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib as mpl
from IPython import embed

#lowpass signal with cutoff of 50 Hz
# detect spikes
# plot channels were spikes had a certain amplitude (and rather are csd than spikes)

class CsdPlot:
    def __init__(self, figure, reader):
        self.reader = reader
        signal = self.reader.voltage_traces[:]
        try:
            ch_ids = self.reader.channel_indices
            labels = self.reader.labels
            fs = self.reader.sampling_frequency
            self.plot(figure, signal, ch_ids, labels, fs)
        except AttributeError:
            self.plot(figure, signal, ch_ids=None, labels=None, fs=10000)

    def plot(self, figure, signal, ch_ids, labels, fs):
        time = np.arange(0, len(signal[0])/fs, 1/fs)
        color_count = 8
        colors = [plt.cm.Pastel2(x) for x in np.linspace(0.0, 1.0, color_count)]

        ax = figure.add_subplot(111)
        if ch_ids is not None:
            for idx, ch_id in enumerate(reversed(ch_ids)):
                if len(labels[idx]) < 3:
                    ax.plot(time[::1250], signal[ch_id][::1250]+(idx*1000), color=colors[idx % color_count], lw=4)

            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
        else:
            for idx in range(len(signal)):
                ax.plot(time[::1250], signal[idx][::1250] + (idx * 1000), color=colors[idx % color_count], lw=4)
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