class PlotManager:

    instance = None

    def __init__(self):
        PlotManager.instance = self
        self.plot_list = []
        self.plot_names = []

    # call this when new plot is created: PlotManager.instance.add_plot(...)
    def add_plot(self, plot, plot_name):
        self.plot_list.append(plot)
        self.plot_names.append(plot_name)

    # call this when a tab with a plot is being closed
    def remove_plot(self, plot, plot_name):
        self.plot_list.remove(plot)
        self.plot_names.remove(plot_name)

    # call this in PlotManagerDialog
    def get_plots(self):
        return self.plot_list
