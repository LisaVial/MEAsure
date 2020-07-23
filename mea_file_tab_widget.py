import os.path
from PyQt5 import QtCore, QtWidgets

from mea_data_reader import MeaDataReader
from mea_file_view import MeaFileView

class MeaFileTabWidget(QtWidgets.QTabWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setTabBarAutoHide(False)

        self.tabCloseRequested.connect(self.on_tab_close_requested)

        self.mea_file_widget_map = dict()

    def show_mea_file_view(self, mea_file):
        if mea_file not in self.mea_file_widget_map.keys():
            mea_file_view = MeaFileView(self, mea_file)
            relative_root, file_name = os.path.split(mea_file)
            if file_name.endswith(".h5"):
                file_name = file_name[:-3]
            self.addTab(mea_file_view, file_name)
            self.mea_file_widget_map[mea_file] = mea_file_view

        self.setCurrentWidget(self.mea_file_widget_map[mea_file])

    @QtCore.pyqtSlot(int)
    def on_tab_close_requested(self, index):
        mea_file_view = self.widget(index)
        if mea_file_view.can_be_closed():
            self.nix_file_widget_map.pop(mea_file_view.mea_file, None)
            self.removeTab(index)
            mea_file_view.close()