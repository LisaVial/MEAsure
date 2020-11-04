class PlotManager:

    instance = None

    def __init__(self):
        PlotManager.instance = self
        self.plot_list = []

    # call this when new plot is created: PlotManager.instance.add_plot(...)
    def add_plot(self, plot):
        self.plot_list.append(plot)

    # call this when a tab with a plot is being closed
    def remove_plot(self, plot):
        self.plot_list.remove(plot)

    # call this in PlotManagerDialog
    def get_plots(self):
        return self.plot_list
