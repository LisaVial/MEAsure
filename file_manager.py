from PyQt5 import QtCore, QtWidgets
import os
class FileManager(QtWidgets.QWidget):

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

        self.auto_detect_meae_file()
        self.auto_detect_sc_file()

    def auto_detect_meae_file(self):
        file = self.mcs_file
        file_without_extension = ".".join(file.split('.')[:-1])
        file_as_meae = file_without_extension + ".meae"
        if os.path.exists(file_as_meae):
            self.meae_path_input.setText(file_as_meae)

    def auto_detect_sc_file(self):
        file = self.mcs_file
        file_without_extension = ".".join(file.split('.')[:-1])
        file_as_sc = file_without_extension + ".result.hdf5"
        if os.path.exists(file_as_sc):
            self.sc_path_input.setText(file_as_sc)

    def get_verified_meae_file(self):
        file = self.meae_path_input.text().strip()
        if os.path.exists(file):
            return file
        else:
            return None

    def get_verified_sc_file(self):
        file = self.sc_path_input.text().strip()
        if os.path.exists(file):
            return file
        else:
            return None

    @QtCore.pyqtSlot()
    def on_meae_path_change_button_pressed(self):
        selectedFile = QtWidgets.QFileDialog.getOpenFileName(self, "Please select Meae file", self.mcs_file_directory,
                                              "Meae files (*.meae)")[0]
        if len(selectedFile) > 0:
            self.meae_path_input.setText(selectedFile)

    @QtCore.pyqtSlot()
    def on_meae_path_remove_button_pressed(self):
        self.meae_path_input.setText("")

    @QtCore.pyqtSlot()
    def on_sc_path_change_button_pressed(self):
        selectedFile = QtWidgets.QFileDialog.getOpenFileName(self, "Please select SC file", self.mcs_file_directory,
                                                             "SC files (*.hdf5)")[0]
        if len(selectedFile) > 0:
            self.sc_path_input.setText(selectedFile)

    @QtCore.pyqtSlot()
    def on_sc_path_remove_button_pressed(self):
        self.sc_path_input.setText("")
