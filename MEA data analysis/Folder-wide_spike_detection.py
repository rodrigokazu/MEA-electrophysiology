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

from class_RAW_NeuronalData import *
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------------- #

# Method definitions #

# ----------------------------------------------------------------------------------------------------------------- #

def folderwide_spike_detection(MEAs_paths):

    for key in MEAs_paths.keys():

        folder = str(MEAs_paths[key]) + "\\"
        MEA = str(key)
        print('Running the analysis for MEA', MEA, 'inside folder', folder)

        raw_timeseries = object_constructor(folder, MEA)

        raw_timeseries.recursive_spike_detection()


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

# ----------------------------------------------------------------------------------------------------------------- #

# Methods testing #

# ----------------------------------------------------------------------------------------------------------------- #

print("\n Welcome to the University of Reading - Brain Embodiment Laboratory (SBS - BEL) \n "
      "This script was designed compute the firing rate of recordings from a folder containing *.mat files. \n "
      "You NEED to have the original *.mat files processed with the MCD_files_export_uV_and_mS_plus_METADATA.m script"
      " \n Your *.mat files must be inside folders named with the MEA number \n")

full_path = input()

MEAs_paths = MEA_path_acquisition(full_path)

folderwide_spike_detection(MEAs_paths)