

class RasterPlot:
    def __init__(self, figure, spike_mat):
        fig = figure
        spike_mat = spike_mat
        self.plot(fig, spike_mat)

    def plot(self, fig, spike_mat):
        fig.eventplot(spike_mat)
        fig.show()