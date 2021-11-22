import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from filtering.filter_settings_widget import FilterSettingsWidget


# This class is to have a filter settings dialog where the user can actually set the settings he/she needs.
class FilterSettingsDialog(QtWidgets.QDialog):  # Setting up of a new class. In the brackets it is defined which
    # PyQt Widget will be the parent of the class.
    """
    The FilterSettingsDialog is opened, once a user presses the Filter button in the MeaFileView. Once the settings are
    set and the okay button is clicked, a new tab will be added to the MeaFileView which shows some visual output of the
    filtering method (new filtered trace vs old unfiltered trace). Also, in the background a QThread is created, which
    enables the GUI to be still responsive, while there are longer computations running in the background
    """
    def __init__(self, parent, allowed_channel_modes, mea_file_exists, meae_path, inital_settings=None):
        # With this function you initialize a class.
        """
        :param parent: This parameter is needed for PyQt -> it tells the program in which other Widget the current
        widget will be embedded.
        :param allowed_channel_modes: This parameter defines if filtering will be done on all channels or only on
        selected channels.
        :param inital_settings: If this parameter is provided, it will be used to preconfigure the settings for
        filtering.
        """
        super().__init__(parent)    # This function is needed correctly initialize this class as it is derived from
        # another class (called its 'super' class, in this case QtWidgets.QDialog)
        # Set the name of the dialog.
        title = 'Filtering'
        self.setWindowTitle(title)
        # Here, mainly the look of the Gui is set up:
        # Basically, PyQt works with widgets (different kinds of buttons, dialogs, etc.) which can be customized.
        # Sometimes these widgets send signals and the signals themselves trigger events, like calling a function.
        # The next few lines are to define the titlebar of the new dialog (where close window, minimize and maximize
        # window buttons are and where the title of a window is shown).
        # Sometimes Qt functions needs a reference to other Qt classes, this is why often there must be several imports
        # in the beginning of the scripts and why the function setWindowFlag has to be called with QtCore.Qt.Customize-
        # WindowHint and then a boolean argument in brackets.
        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        # Here, the size of the window is set.
        width = 400
        height = 400
        self.setFixedSize(width, height)

        # For widgets in PyQt there have to be layouts to which the widgets are added. The layout defines where things
        # will be put inside your widget or dialog.
        main_layout = QtWidgets.QVBoxLayout(self)
        # QVBoxlayout will put the items vertically and needs the class itself as parent, so you have to call it with
        # 'self' in round brackets
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        # With setAlignment() it is set if buttons and widget will be portrayed in center, on the left or right, on the
        # top or the bottom.

        # In this case, the widget for the buttons is in an extra script, but if there are not many settings, sometimes
        # the widget will be defined in the script of the dialog itself. If a widget is defined outside the current
        # script, it has to be called like a function and imported on the top of the current script.
        self.filter_settings_widget = FilterSettingsWidget(self, allowed_channel_modes, mea_file_exists, meae_path,
                                                           inital_settings)
        main_layout.addWidget(self.filter_settings_widget)

        self.meae_filename = None
        self.append_to_existing_file = False

        # Here two small widgets are defined inside of this script. They are a okay and cancel button to execute or
        # abort filtering.
        # Line 61 defines which widget will be used. Here, we use a button.
        self.okay_button = QtWidgets.QPushButton(self)
        # Line 63 defines which text will be shown inside of the button.
        self.okay_button.setText('Execute')
        # Line 67 links the signal of the button press (clicked) to the function on_okay_clicked, which is defined in
        # the bottom of the script. By connecting a signal to a function the function has to be called in the brackets
        # and without brackets behind themselves.
        self.okay_button.clicked.connect(self.on_okay_clicked)
        # Line 69 simply adds the widget (the okay_button) to the main_layout
        main_layout.addWidget(self.okay_button)

        # same procedure as for the okay button is applied for the cancel button.
        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText('Abort')
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        main_layout.addWidget(self.cancel_button)

    def get_settings(self):
        """
        This function gets the settings which the user has set.
        :return: variables of the filter_settings script
        """
        return self.filter_settings_widget.get_settings()

    def on_okay_clicked(self):
        """
        This function initializes the filtering thread.
        :return: By self.accept() a signal is sent. In this case a variable will be set from 0 to 1, which can be
        checked by the MeaFileView to trigger adding a new tab to the MeaFileView Widget (check this script to see
        more).
        """
        self.accept()

    def on_cancel_clicked(self):
        """
        This function cancels filtering.
        :return: By self.accept() a signal is sent. In this case a variable will be 0, which is also checked by the
        MeaFileView and filtering will therefore not be initialized.
        """
        self.reject()