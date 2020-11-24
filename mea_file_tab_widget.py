import os.path
from PyQt5 import QtCore, QtWidgets

from mea_file_view import MeaFileView


# This widget handles the portrayal of several opened mea recordings. When a user opens another Mea recording, it will
# be added as a tab.
class MeaFileTabWidget(QtWidgets.QTabWidget):

    def __init__(self, parent):
        super().__init__(parent)

        # similiar to the WindowFlags, we have to tell Qt, what is allowed to do with the tabs
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setTabBarAutoHide(False)

        # once a user tries to close a tab, we have to check whether or not there are some tasks (QThreads) running in
        # the tab
        self.tabCloseRequested.connect(self.on_tab_close_requested)

        # by using a dictionary, we have a way to keep an overview, which mea files are opened
        self.mea_file_widget_map = dict()

    # this function is triggered once a user double clicks on a mea recording of the data_list_view
    def show_mea_file_view(self, mea_file):
        # first, we check, if this mea recording is already opened as a tab. If it is, we will not open it again, but
        # rather jump to the tab, which is already opened and has had the same recording file name
        if mea_file not in self.mea_file_widget_map.keys():
            mea_file_view = MeaFileView(self, mea_file)     # this adds the portrayal of a new recording as a new tab
            relative_root, file_name = os.path.split(mea_file)   # here, we get the filename of the mea recording
            if file_name.endswith(".h5"):   # this condition is just to portray the filename without the data extension
                # at the top(= tab) of this recording
                file_name = file_name[:-3]
            self.addTab(mea_file_view, file_name)   # here the tab is actually added
            self.mea_file_widget_map[mea_file] = mea_file_view # and here we "remember" that we have opened it
        # here, we make sure that the latest opened file is the one which is also shown to the user
        self.setCurrentWidget(self.mea_file_widget_map[mea_file])

    @QtCore.pyqtSlot(int)
    def on_tab_close_requested(self, index):    # similar procedure if we want to close a tab
        mea_file_view = self.widget(index)  # this is the currently opened tab of a mea recording

        if mea_file_view.can_be_closed(): # the function "can_be_closed()" can be found in the MeaFileView script and
            # if there is no task running currently, it will return True
            self.mea_file_widget_map.pop(mea_file_view.mea_file, None)  # here we get rid of the dictionary entry
            self.removeTab(index)   # here we close the tab
            mea_file_view.close()   # and here we close the MeaFileView
        #else: at least one tab in mea_file_view is running a thread => ignore close request to avoid crashes