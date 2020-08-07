import McsPy
import McsPy.McsData
import h5py


class MeaDataReader:
    def __init__(self):
        pass

    def open_mea_file(self, path):
        # file = h5py.File(path, 'r')
        file = McsPy.McsData.RawData(path)
        return file
