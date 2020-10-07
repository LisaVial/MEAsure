import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import os.path
from IPython import embed


class DataListView(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # setting up labels for GUI portrayal
        self.selected_folder_label = QtWidgets.QLabel("")
        self.current_folder = ""

        # implementation of button to set folder directory
        self.select_folder_button = QtWidgets.QPushButton("...")
        self.select_folder_button.setFixedSize(24, 24)
        self.select_folder_button.pressed.connect(self.on_select_folder_button_pressed)

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
        data_files, mea_indices = self.get_data()
        print(mea_indices)
        for idx, file in enumerate(data_files):
            self.file_list.addItem(file)
            if idx in mea_indices:
                self.file_list.item(idx).setBackground(QtGui.QColor(0, 134, 153))
                self.file_list.item(idx).setForeground(QtGui.QColor("white"))

    # function that scans absolute and relative paths of data
    def get_data(self):
        # scan recursively for (which file format do we have?) files
        found_files = []
        meae_files = []
        for root, sub_folders, files in os.walk(self.current_folder):
            for file in files:
                absolute_path = os.path.join(root, file)
                relative_path = os.path.relpath(absolute_path, self.current_folder)
                if file.endswith(".h5") or file.endswith('result.hdf5'):
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



