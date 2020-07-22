import PyQt5.QtCore as QtCore
import json


def load_settings_from_file(path):
    try:
        d = json.load(path)
        settings = Settings()
        settings.last_folder = d["last_folder"]
        settings.main_window_geometry = QtCore.QByteArray(bytearray(d["main_window_geometry"], "ascii"))
        settings.main_window_state = QtCore.QByteArray(bytearray(d["main_window_state"], "ascii"))
        return settings
    except:
        None


class Settings:

    def __init__(self):
        self.last_folder = ""
        self.main_window_geometry = bytearray()
        self.main_window_state = bytearray()

    def to_dict(self):
        d = dict()
        d["last_folder"] = self.last_folder
        d["main_window_geometry"] = bytearray(self.main_window_geometry).decode("ascii")
        d["main_window_state"] = bytearray(self.main_window_state).decode("ascii")
        return d

    def save(self, path):
        json.dump(self.to_dict(), path)