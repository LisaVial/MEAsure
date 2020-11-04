class PlotManager:

    instance = None

    def __init__(self):
        PlotManager.instance = self
        self.plot_list = []
        self.list_view = None

    def set_plot_list_view(self, list_view):
        self.list_view = list_view

    # call this when new plot is created: PlotManager.instance.add_plot(...)
    def add_plot(self, plot_widget):
        self.plot_list.append(plot_widget)
        if self.list_view:
            self.list_view.update_list()

    # call this when a tab with a plot is being closed
    def remove_plot(self, plot):
        self.plot_list.remove(plot)
        if self.list_view:
            self.list_view.update_list()

    # call this in PlotManagerDialog
    def get_plots(self):
        return self.plot_list
