import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .raster_plot_settings import RasterplotSettings

class RasterplotSettingsWidget(QtWidgets.QGroupBox):

    def __init__(self, parent, settings=None):
        super().__init__(parent)

        self.setTitle('Settings')
        group_box_layout = QtWidgets.QGridLayout(self)

