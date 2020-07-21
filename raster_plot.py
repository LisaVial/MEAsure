

class RasterPlot:
    def __init__(self, figure, spike_mat):
        fig = figure
        spike_mat = spike_mat
        fig.eventplot(spike_mat)
        fig.show()