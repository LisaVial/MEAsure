import McsPy
import McsPy.McsData


class MeaDataReader:
    def __init__(self):
        pass

    def open_mea_file(self, path):
        file = McsPy.McsData.RawData(path)
        return file
