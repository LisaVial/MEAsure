import os
import numpy as np
import h5py
from IPython import embed


class SCDataReader:
    def __init__(self, path):
        self.folder, self.cluster_filename = os.path.split(path)
        # only cut out last two tokens (e.g. 'clusters', 'hdf5') leave the rest
        self.filename_prefix = '.'.join(self.cluster_filename.split('.')[:-2])

        self.file = h5py.File(path, 'r')
        self.spiketimes = self.retrieve_spiketimes()
        self.retrieve_mua_spikes()

    def retrieve_mua_spikes(self):
        mua_filename = self.filename_prefix + ".mua.hdf5"
        mua_filepath = os.path.join(self.folder, mua_filename)
        if os.path.exists(mua_filepath):
            mua_file = h5py.File(mua_filepath, 'r')
            same_len_keys = []
            for key in list(mua_file['spiketimes'].keys()):
                if 'elec' in key:
                    if len(key) == 6:
                        current_key = key[:5] + '00' + key[-1:]
                        same_len_keys.append(current_key)
                    elif len(key) == 7:
                        # ToDo: check, if keys are correct
                        current_key = key[:5] + '0' + key[-2:]
                        same_len_keys.append(current_key)
                    else:
                        same_len_keys.append(key)

            indices = np.argsort(same_len_keys)

            sorted_mua_spiketimes = []
            sorted_mua_amplitudes = []
            for idx in indices:
                key = 'elec_' + str(idx)
                if key in list(mua_file['spiketimes'].keys()):
                    sorted_mua_spiketimes.append(mua_file['spiketimes'][key][:])
                if key in list(mua_file['amplitudes'].keys()):
                    sorted_mua_amplitudes.append(mua_file['amplitudes'][key][:])
            return sorted_mua_spiketimes, sorted_mua_amplitudes
        else:
            return None

    def retrieve_spatial_mat(self):
        spatial_filename = self.filename_prefix + ".basis.hdf5"
        spatial_filepath = os.path.join(self.folder, spatial_filename)
        if os.path.exists(spatial_filepath):
            spatial_file = h5py.File(spatial_filepath, 'r')
            spatial_mat = spatial_file['spatial']
            return spatial_mat
        else:
            return None

    def retrieve_thresholds(self):
        basis_filename = self.filename_prefix + ".basis.hdf5"
        basis_filepath = os.path.join(self.folder, basis_filename)
        if os.path.exists(basis_filepath):
            basis_file = h5py.File(basis_filepath, 'r')
            thresholds = basis_file['thresholds']
            return thresholds
        else:
            return None

    def retrieve_spiketimes(self):
        same_len_keys = []
        for key in list(self.file.keys()):
            if 'times' in key:
                if len(key) == 6:
                    current_key = key[:5] + '00' + key[-1:]
                    same_len_keys.append(current_key)
                elif len(key) == 7:
                    current_key = key[:5] + '0' + key[-2:]
                    same_len_keys.append(current_key)
                else:
                    same_len_keys.append(key)
        indices = np.argsort(same_len_keys)

        sorted_spiketimes = []
        for idx in indices:
            key = 'times_' + str(idx)
            if key in list(self.file.keys()):
                sorted_spiketimes.append(self.file[key][:])
        return sorted_spiketimes
