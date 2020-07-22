import McsPy
import McsPy.McsData


class MeaDataViewer:
    def __init__(self, path):
        self.file_path = path
        self.file = self.open_mea_file()

    def open_mea_file(self):
        file = McsPy.McsData.RawData(self.file_path)
        return file
