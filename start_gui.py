import sys
import os
import ctypes
import PyQt5.QtWidgets as QtWidgets


from main_window import MainWindow


if os.name == 'nt':
    my_app_id = u'lv.meaanalyzer.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

# the following lines create an exception hook
# which allows to output Python exceptions while PyQt is running
# taken from: https://stackoverflow.com/a/43039363/8928024
sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = my_exception_hook
# end of exception hook creation

application = QtWidgets.QApplication(sys.argv)
mainWindow = MainWindow('MEAsure')
mainWindow.show()

application.setActiveWindow(mainWindow)
sys.exit(application.exec())