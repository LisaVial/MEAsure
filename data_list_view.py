import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import os.path
from IPython import embed
import numpy as np

from meae_data_reader import MeaeDataReader


# This widget scans for files in different folders via os.path and adds them to a list of which the user can
# open his/her desired .h5 file
class DataListView(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # setting up labels for GUI portrayal
        self.selected_folder_label = QtWidgets.QLabel("")
        self.current_folder = ""

        # implementation of button to set folder directory. The directory will be saved, so once its set it will be
        # shown automatically when the program is opened again
        self.select_folder_button = QtWidgets.QPushButton("...")
        self.select_folder_button.setFixedSize(24, 24)
        self.select_folder_button.pressed.connect(self.on_select_folder_button_pressed)

        # the DataList itself is a QListWidget
        self.file_list = QtWidgets.QListWidget(self)

        # layout
        main_layout = QtWidgets.QVBoxLayout(self)
        folder_path_layout = QtWidgets.QHBoxLayout()
        folder_path_layout.addWidget(self.selected_folder_label)
        folder_path_layout.addWidget(self.select_folder_button)
        main_layout.addLayout(folder_path_layout)
        main_layout.addWidget(self.file_list)

    # function, that executes folder selection, once the according button was pressed
    @QtCore.pyqtSlot()
    def on_select_folder_button_pressed(self):
        selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Please choose a directory")
        if len(selected_folder) > 0:
            self.set_current_folder(selected_folder)

    # function that searches for the data in the choosen directory
    def set_current_folder(self, folder):
        self.current_folder = folder
        self.selected_folder_label.setText(folder)
        self.file_list.clear()
        data_files, meae_indices = self.get_data()
        for idx, file in enumerate(data_files):
            self.file_list.addItem(file)
            tool_tip = "No .meae file found."
            self.file_list.item(idx).setToolTip(tool_tip)
            if idx in meae_indices:
                self.file_list.item(idx).setBackground(QtGui.QColor(0, 134, 153))
                self.file_list.item(idx).setForeground(QtGui.QColor("white"))
                self.file_list.item(idx).setToolTip(tool_tip)
                file_without_extension = ".".join(file.split('.')[:-1])
                mea_file = self.current_folder + file_without_extension + ".meae"
                if os.path.exists(mea_file):
                    reader = MeaeDataReader(mea_file)
                    keys = list(reader.file.keys())
                    spiketimes_indices_key_indices = [int(i) for i, key in enumerate(keys) if 'spiketimes_indices' in
                                                      key]
                    spiketimes_indices_keys = [keys[idx] for idx in spiketimes_indices_key_indices]
                    spiketimes_key_indices = np.asarray(spiketimes_indices_key_indices) - 2
                    spiketimes_keys = [keys[idx] for idx in spiketimes_key_indices]
                    if len(spiketimes_keys) > 1:
                        for k_idx, key in enumerate(keys):
                            if key in spiketimes_keys or key in spiketimes_indices_keys and k_idx == 0:
                                num_of_spiketimes = len(spiketimes_keys)
                                tool_tip_keys = [key for key in keys if 'spiketimes' not in key]
                                tool_tip_keys.append(str(int(num_of_spiketimes)) +
                                                     ' spiketimes and spike indices found')
                                tool_tip = "Keys: " + ", ".join(tool_tip_keys)
                                self.file_list.item(idx).setToolTip(tool_tip)
                            else:
                                continue
                    else:
                        tool_tip = "Keys: " + ", ".join(keys)
                        self.file_list.item(idx).setToolTip(tool_tip)

    # function that scans absolute and relative paths of data
    def get_data(self):
        # scan recursively for (which file format do we have?) files
        found_files = []
        meae_files = []
        for root, sub_folders, files in os.walk(self.current_folder):
            for file in files:
                absolute_path = os.path.join(root, file)
                relative_path = os.path.relpath(absolute_path, self.current_folder)
                if relative_path.startswith('$RECYCLE.BIN'):
                    continue
                if file.endswith(".h5"):
                    found_files.append(relative_path)
                if file.endswith(".meae"):
                    meae_files.append(relative_path)

        mea_indices = []
        for index, file in enumerate(found_files):
            if '.' in file:
                file_without_extension = ".".join(file.split('.')[:-1])
                file_as_meae = file_without_extension + ".meae"
                if file_as_meae in meae_files:
                    mea_indices.append(index)

        return found_files, mea_indices
