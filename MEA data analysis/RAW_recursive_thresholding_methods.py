# Brain Embodiment Laboratory #
# University of Reading #

# BEL's Script for spike extraction via thresholding in RAW recordings of MCD files#
# This program is meant to be used after the files were treated with the export_electrode_raw_data_mcd#

# ----------------------------------------------------------------------------------------------------------------- #

# Written by Rodrigo Kazu #
# Any enquiries to r.siqueiradesouza@pgr.reading.ac.uk #

# ----------------------------------------------------------------------------------------------------------------- #

# First block import the relevant libraries and initialises the important variables #

# ----------------------------------------------------------------------------------------------------------------- #

from class_RAW_NeuronalData import RAW_NeuronalData
import gc
import numpy as np
from pathlib import Path
from scipy import sparse as sp
import time

# ----------------------------------------------------------------------------------------------------------------- #

# Method definitions #

# ----------------------------------------------------------------------------------------------------------------- #

def folderwide_spike_detection(MEAs_paths):

    for key in MEAs_paths.keys():

        folder = str(MEAs_paths[key]) + "\\"
        MEA = str(key)
        print('Running the analysis for MEA', MEA, 'inside folder', folder)

        raw_timeseries = object_constructor(folder, MEA)

        recursive_spike_detection(raw_timeseries)


def MEA_path_acquisition(full_path):

    path = Path(full_path)
    MEAs_paths = {}

    for path in path.iterdir():

        if path.is_dir():

            path_to_string = str(path)

            if path_to_string[-5:].isdigit():

                key = path_to_string[-5:]
                MEAs_paths[key] = str(path_to_string)

            elif path_to_string[-4:].isdigit():

                key = path_to_string[-4:]
                MEAs_paths[key] = str(path_to_string)

    return MEAs_paths


def object_constructor(folder, MEA):

    # Initialising the RAW_NeuronalData object and imports data files. #

    uv_data = folder + MEA + '_RAW_voltage_data.mat'
    time_array = folder + MEA + '_time_array_ms.mat'
    channelids = folder + MEA + '_correct_electrode_order.mat'

    print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling

    raw_data = RAW_NeuronalData(uv_data, time_array, channelids)

    print('RAW_NeuronalData object created!')

    print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling

    return raw_data


def recursive_spike_detection(raw_timeseries):

    spiketimes = {}  # Dictionary that will contain the detected spiketimes
    valid_channels = list()  # List of valid channels, with 4 or more spikes and visually inspected
    threshold_array = {}  # Dictionary that will contain the threshold computations
    recur_spiketimes = {}
    recur_spikevoltages = {}
    detection_number = {}
    print('Used dicts created.')
    flagmatrix = sp.csr_matrix([90, 6000000])  # This matrix will contain the positions to be ignored #

    # ------------------------------------------------------------------------------------------------------------ #

    for key in raw_timeseries.mcd_data:  # Creates the threshold lists

        if key != 'ms':

            threshold_array[key] = list()

    for key in raw_timeseries.mcd_data:

        if key != 'ms':

            size = raw_timeseries.mcd_data[key].size
            threshold = -5.5 * np.std(raw_timeseries.mcd_data[key])  # Sets the threshold in 5.5 STD
            threshold_array[key].append(threshold)
            print('Threshold for channel', key, 'is', threshold)

            for spikes in range(0, size - 1):  # Flags detects spikes

                if raw_timeseries.mcd_data[key][spikes] < threshold:

                    flagmatrix[int(key)][spikes] = True
                    continue

    # File handling #

    f = open('.\..\Analysis_Output.txt', 'w')
    f.write(str(flagmatrix))
    f.close()

    # Memory cleaning #

    del raw_timeseries
    gc.collect()
    print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling

# ----------------------------------------------------------------------------------------------------------------- #

# Methods testing #

# ----------------------------------------------------------------------------------------------------------------- #

print("\n \n Welcome to the University of Reading - Brain Embodiment Laboratory (SBS - BEL) \n \n \n This script was designed compute the firing rate of recordings from a folder containing *.mat files. \n \n \n You NEED to have the original *.mat files processed with the MCD_files_export_uV_and_mS_plus_METADATA.m script \n \n \n Your *.mat files must be inside folders named with the MEA number \n \n \n")

full_path = input()

MEAs_paths = MEA_path_acquisition(full_path)

folderwide_spike_detection(MEAs_paths)

