# Brain Embodiment Laboratory #
# University of Reading #

# -----------------------------------------------------------------------------------------------------------------#

# This script is an optimised version, it does not deepcopy my RAW_NeuronalData object #

# -----------------------------------------------------------------------------------------------------------------#

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

# loadmat will import your *.mat datafile as a dictionary, PASTE YOUR FOLDER HERE. #

# ----------------------------------------------------------------------------------------------------------------- #

# Useful advice: Problem is with the string. Here, \U starts an eight-character Unicode escape, such as '\U00014321`. #
# In your code, the escape is followed by the character 's', which is invalid. #
# Duplicate all the backslashes #

print("\n \n Welcome to the University of Reading - Brain Embodiment Laboratory (SBS - BEL) \n \n \n This script was designed compute the firing rate of recordings from a folder containing *.mat files. \n \n \n You NEED to have the original *.mat files processed with the MCD_files_export_uV_and_mS_plus_METADATA.m script \n \n \n Your *.mat files must be inside folders named with the MEA number \n \n \n")

full_path = input()

path = Path(full_path)

MEAs_paths = {}

for path in path.iterdir():

    if path.is_dir():

        path_to_string = str(path)
        key = path_to_string[-5:]
        MEAs_paths[key] = path

# ----------------------------------------------------------------------------------------------------------------- #

# This block runs your folder grabbing files. #

# ----------------------------------------------------------------------------------------------------------------- #

for path in path.iterdir():

    if path.is_dir():

        path_to_string = str(path)

        if path_to_string[-5:].isdigit():

            key = path_to_string[-5:]
            MEAs_paths[key] = str(path_to_string)

        else:

            key = path_to_string[-4:]
            MEAs_paths[key] = str(path_to_string)

for key in MEAs_paths.keys():

    folder = str(MEAs_paths[key]) + '\\'
    MEA = str(key)
    print('Running the analysis for MEA', MEA, 'inside folder', folder)

    # --------------------------------------------------------------------------------------------------------------- #

    # Second Block #

    # Initialises the object of NeuronalData and imports the data files. #

    # --------------------------------------------------------------------------------------------------------------- #

    uv_data = folder + MEA + '_RAW_voltage_data.mat'
    time_array = folder + MEA + '_time_array_ms.mat'
    channelids = folder + MEA + '_correct_electrode_order.mat'

    print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling
    raw_timeseries = RAW_NeuronalData(uv_data, time_array, channelids)

    print('RAW_NeuronalData object created!')

    print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling

    # ------------------------------------------------------------------------------------------------------------ #

    # 20 Hz High Pass filtering #

    # ------------------------------------------------------------------------------------------------------------ #

    raw_timeseries = raw_timeseries.highpass()

    print('Data filtered (20Hz High Pass)!')

    print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling

    # ------------------------------------------------------------------------------------------------------------ #

    # voltagedata_cell is the key in the imported dictionary #
    # The first index after it stands for the matrix line, the second one for the column #

    # Column ZERO has all the channel names, already in the correct order #
    # ---Last two indexes come from the weird way the *.mat is imported--- #

    # ------------------------------------------------------------------------------------------------------------ #

    # Creates a set of important data structures to be used by the function spike_detection#

    # ------------------------------------------------------------------------------------------------------------ #

    spiketimes = {}  # Dictionary that will contain the detected spiketimes
    valid_channels = list()  # List of valid channels, with 4 or more spikes and visually inspected
    threshold_array = {}  # Dictionary that will contain the threshold computations
    recur_spiketimes = {}
    recur_spikevoltages = {}
    detection_number = {}
    print('Used dicts created.')
    flagmatrix = sp.csr_matrix([90, 6000000])  # This matrix will contain the positions to be ignored #

    # ------------------------------------------------------------------------------------------------------------ #

    for key in raw_timeseries.mcd_data:

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
                    break

    f = open('.\..\Analysis_Output.txt', 'w')
    f.write(str(flagmatrix))
    f.close()

    del raw_timeseries
    gc.collect()
    print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling
