import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .raster_plot_settings import RasterplotSettings


class RasterplotDialog(QtWidgets.QDialog):
    def __init__(self, settings=None):
        title = 'Settings'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.width = 300
        self.height = 200

        self.setWindowTitle(title)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        self.spiketimes_selection_combo_box = QtWidgets.QComboBox(self)

        self.spiketimes_selection_combo_box.addItem('.meae files')
        self.spiketimes_selection_combo_box.addItem('SC result files')

        self.spiketimes_selection_combo_box.setEditable(True)
        self.spiketimes_selection_combo_box.lineEdit().setReadOnly(True)

        self.spiketimes_selection_combo_box.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.spiketimes_selection_combo_box.currentIndexChanged.connect(self.spiketimes_selection_changed)
        main_layout.addWidget(self.filter_combo_box)

        self.spiketimes_selection_textbox = QtWidgets.QLineEdit(self)
        self.spiketimes_selection_textbox.setAlignment(QtCore.Qt.AlignCenter)
        self.textbox_label = QtWidgets.QLabel('Data path of used spiketimes: ')
        main_layout.addWidget(self.single_cutoff_textbox)
        main_layout.addWidget(self.textbox_label)

        if not settings:
            # create default settings
            settings = RasterplotSettings()

            # initialise widgets with settings
        self.set_settings(settings)

    def set_settings(self, settings):
        self.spiketimes_selection_combo_box.setCurrentIndex(settings.mode)
        if settings.mode == 0:
            self.spiketimes_selection_textbox.setText(
                str(settings.lower_cutoff))  # set entry index by reading mode (index) from settings
