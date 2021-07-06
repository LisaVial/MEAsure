from PyQt5 import QtCore, QtWidgets
import os
import json

# This widget enables the user to set paths to .meae files or SpyKING CIRCUS (SC) result files which will then be used
# for plotting
class FileManager(QtWidgets.QWidget):

    class Cache:
        storage_file = "./file-path-cache.json"

        def __init__(self):
            self.path_group_list = []
            self.load()

        def load(self):
            try:
                with open(FileManager.Cache.storage_file, 'r') as file:
                    self.path_group_list = json.load(file)
            except:
                self.path_group_list = []

        def save(self):
            with open(FileManager.Cache.storage_file, 'w') as file:
                json.dump(self.path_group_list, file)

        def update_entry(self, mcs_path, mea_path, sc_cluster_path, sc_base_path):

            if mea_path is None:
                mea_path = ""
            if sc_cluster_path is None:
                sc_cluster_path = ""
            if sc_base_path is None:
                sc_base_path = ""

            existing_path_group = None
            for path_group in self.path_group_list:
                if path_group[0] == mcs_path:
                    existing_path_group = path_group
                    break

            if existing_path_group is not None:
                self.path_group_list.remove(existing_path_group)

            updated_path_group = (mcs_path, mea_path, sc_cluster_path, sc_base_path)
            self.path_group_list.append(updated_path_group)

        def get_verified_paths(self, mcs_path):
            verified_paths = ["", "", ""]


            for path_group in self.path_group_list:
                if path_group[0] == mcs_path and len(path_group) == 4:

                    for index, path in enumerate(path_group[1:]):
                        if path is not None and os.path.exists(path):
                            verified_paths[index] = path

                    break

            return tuple(verified_paths)


    def __init__(self, mea_file_view, mcs_file):
        super().__init__(mea_file_view)
        self.mea_file_view = mea_file_view
        self.mcs_file = mcs_file

        self.mcs_file_directory, self.mcs_file_name = os.path.split(self.mcs_file)

        # layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        mcs_layout = QtWidgets.QHBoxLayout()
        mcs_label = QtWidgets.QLabel(self)
        mcs_label.setText("MCS file:")
        mcs_layout.addWidget(mcs_label)
        mcs_path_label = QtWidgets.QLabel(self)
        mcs_path_label.setText(mcs_file)
        mcs_layout.addWidget(mcs_path_label)
        main_layout.addLayout(mcs_layout)

        meae_layout = QtWidgets.QHBoxLayout()
        meae_label = QtWidgets.QLabel(self)
        meae_label.setText("MEAE file:")
        meae_layout.addWidget(meae_label)
        self.meae_path_input = QtWidgets.QLineEdit(self)
        self.meae_path_input.setText("")
        meae_layout.addWidget(self.meae_path_input)
        meae_path_change_button = QtWidgets.QPushButton(self)
        meae_path_change_button.setText("...")
        meae_path_change_button.pressed.connect(self.on_meae_path_change_button_pressed)
        meae_layout.addWidget(meae_path_change_button)
        meae_path_remove_button = QtWidgets.QPushButton(self)
        meae_path_remove_button.setText("-")
        meae_path_remove_button.pressed.connect(self.on_meae_path_remove_button_pressed)
        meae_layout.addWidget(meae_path_remove_button)
        main_layout.addLayout(meae_layout)

        sc_layout = QtWidgets.QHBoxLayout()
        sc_label = QtWidgets.QLabel(self)
        sc_label.setText("SC file:")
        sc_layout.addWidget(sc_label)
        self.sc_path_input = QtWidgets.QLineEdit(self)
        self.sc_path_input.setText("")
        sc_layout.addWidget(self.sc_path_input)
        sc_path_change_button = QtWidgets.QPushButton(self)
        sc_path_change_button.setText("...")
        sc_path_change_button.pressed.connect(self.on_sc_path_change_button_pressed)
        sc_layout.addWidget(sc_path_change_button)
        sc_path_remove_button = QtWidgets.QPushButton(self)
        sc_path_remove_button.setText("-")
        sc_path_remove_button.pressed.connect(self.on_sc_path_remove_button_pressed)
        sc_layout.addWidget(sc_path_remove_button)
        main_layout.addLayout(sc_layout)

        sc_base_file_layout = QtWidgets.QHBoxLayout()
        sc_base_file_label = QtWidgets.QLabel(self)
        sc_base_file_label.setText("base file in the SC folder:")
        sc_base_file_layout.addWidget(sc_base_file_label)
        self.sc_base_file_input = QtWidgets.QLineEdit(self)
        self.sc_base_file_input.setText("")
        sc_base_file_layout.addWidget(self.sc_base_file_input)
        sc_base_file_change_button = QtWidgets.QPushButton(self)
        sc_base_file_change_button.setText("...")
        sc_base_file_change_button.pressed.connect(self.on_sc_base_file_path_change_button_pressed)
        sc_base_file_layout.addWidget(sc_base_file_change_button)
        sc_base_file_remove_button = QtWidgets.QPushButton(self)
        sc_base_file_remove_button.setText("-")
        sc_base_file_remove_button.pressed.connect(self.on_sc_base_file_path_remove_button_pressed)
        sc_base_file_layout.addWidget(sc_base_file_remove_button)
        main_layout.addLayout(sc_layout)
        main_layout.addLayout(sc_base_file_layout)

        # load file paths from cache
        self.cache = FileManager.Cache()
        verified_paths = self.cache.get_verified_paths(self.mcs_file)

        if len(verified_paths[0]) > 0:
            self.meae_path_input.setText(verified_paths[0])
        else:
            self.auto_detect_meae_file()

        if len(verified_paths[1]) > 0:
            self.sc_path_input.setText(verified_paths[1])
        else:
            self.auto_detect_sc_file()

        if len(verified_paths[2]) > 0:
            self.sc_base_file_input.setText(verified_paths[2])

    def update_path_cache(self, save=True):
        self.cache.update_entry(self.mcs_file, self.get_verified_meae_file(),
                                self.get_verified_sc_file(), self.get_verified_sc_base_file())
        if save:
            self.cache.save()

    # This function automatically detects the .meae file if it is in the same folder as the normal .h5 file (with the
    # same filename except for the file extension).
    def auto_detect_meae_file(self):
        file = self.mcs_file
        file_without_extension = ".".join(file.split('.')[:-1])
        file_as_meae = file_without_extension + ".meae"
        if os.path.exists(file_as_meae):
            self.meae_path_input.setText(file_as_meae)

    # This function automatically detects the SC file if it is in the same folder as the normal .h5 file (with the
    # same filename except for the file extension).
    def auto_detect_sc_file(self):
        file = self.mcs_file
        file_without_extension = ".".join(file.split('.')[:-1])
        file_as_sc = file_without_extension + ".clusters.hdf5"
        if os.path.exists(file_as_sc):
            self.sc_path_input.setText(file_as_sc)

    # This function verifies if the file with the given filepath really exists
    def get_verified_meae_file(self):
        file = self.meae_path_input.text().strip()
        if os.path.exists(file):
            return file
        else:
            return None

    # This function verifies if the file with the given filepath really exists
    def get_verified_sc_file(self):
        file = self.sc_path_input.text().strip()
        if os.path.exists(file):
            return file
        else:
            return None

    def get_verified_sc_base_file(self):
        file = self.sc_base_file_input.text().strip()
        if os.path.exists(file):
            return file
        else:
            return None

    @QtCore.pyqtSlot()
    def on_sc_base_file_path_remove_button_pressed(self):
        self.sc_base_file_input.setText("")
        self.update_path_cache()

    @QtCore.pyqtSlot()
    def on_sc_base_file_path_change_button_pressed(self):
        selectedFile = QtWidgets.QFileDialog.getOpenFileName(self, "Please select SC base file",
                                                             self.mcs_file_directory, "SC files (*.h5)")[0]
        if len(selectedFile) > 0:
            self.sc_base_file_input.setText(selectedFile)
            self.update_path_cache()

    # This function allows a filepath selection dialog to open, once the mea_path_change_button is pressed
    @QtCore.pyqtSlot()
    def on_meae_path_change_button_pressed(self):
        selectedFile = QtWidgets.QFileDialog.getOpenFileName(self, "Please select Meae file", self.mcs_file_directory,
                                              "Meae files (*.meae)")[0]
        if len(selectedFile) > 0:
            self.meae_path_input.setText(selectedFile)
            self.update_path_cache()

    # This function removes a filepath, once the mea_path_remove_button is pressed
    @QtCore.pyqtSlot()
    def on_meae_path_remove_button_pressed(self):
        self.meae_path_input.setText("")
        self.update_path_cache()

    # This function allows a filepath selection dialog to open, once the sc_path_change_button is pressed
    @QtCore.pyqtSlot()
    def on_sc_path_change_button_pressed(self):
        selectedFile = QtWidgets.QFileDialog.getOpenFileName(self, "Please select SC file", self.mcs_file_directory,
                                                             "SC files (*.hdf5)")[0]
        if len(selectedFile) > 0:
            self.sc_path_input.setText(selectedFile)
            self.update_path_cache()

    # This function removes a filepath, once the sc_path_remove_button is pressed
    @QtCore.pyqtSlot()
    def on_sc_path_remove_button_pressed(self):
        self.sc_path_input.setText("")
        self.update_path_cache()
