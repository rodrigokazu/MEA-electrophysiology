# Brain Embodiment Laboratory #
# University of Reading #

# -----------------------------------------------------------------------------------------------------------------#

# BEL's Script to compute firing rates of cultured neuronal networks as MCD files#
# Use after the files were treated with the MCD_files_export_uV_and_mS_plus_METADATA script provided#

# ----------------------------------------------------------------------------------------------------------------- #

# Written by Rodrigo Kazu #
# Any enquiries to r.siqueiradesouza@pgr.reading.ac.uk #

# ----------------------------------------------------------------------------------------------------------------- #

# First block import the relevant libraries and initialises the important variables #

# ----------------------------------------------------------------------------------------------------------------- #

from class_SPKS_NeuronalData import SPKS_NeuronalData
from copy import deepcopy
import datetime
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------------- #

# User input acquisition  #

# ----------------------------------------------------------------------------------------------------------------- #


print("\n \n Welcome to the University of Reading - Brain Embodiment Laboratory (SBS - BEL) \n \n \n "
      "This script was designed compute the firing rate of recordings from a folder containing *.mat files. \n \n "
      "You NEED to have the original *.mat files processed with the MCD_files_export_uV_and_mS_plus_METADATA.m script"
      " \n \n Your *.mat files must be inside folders named with the MEA number. \n \n "
      "Please insert the full path of that folder here. \n \n ")

full_path = input()

path = Path(full_path)

MEAs_paths = {}

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

# Writes the analysis into a *.txt file #

file = full_path + "\Debug_Output_ISI.txt"
f = open(file, 'w')
f.write("Folder analysed: " + full_path)
f.write(str(datetime.datetime.now().strftime(" | Date: %d-%m-%y Time: %H-%M \n \n")))

for key in MEAs_paths.keys():

    folder = str(MEAs_paths[key]) + '\\'
    MEA = str(key)

# ----------------------------------------------------------------------------------------------------------------- #

# Then initialises the object of NeuronalData and imports the data files. #

# ----------------------------------------------------------------------------------------------------------------- #

    shapedata = folder + MEA + '_spikevalues_uV.mat'
    time_array = folder + MEA + '_time_array_ms.mat'
    channelids = folder + MEA + '_correct_electrode_order.mat'
    occurrence_ms = folder + MEA + '_spiketimes_ms.mat'

    spike_data = SPKS_NeuronalData(shapedata, time_array, occurrence_ms, channelids)

#    f.write(occurrence_ms)

# ----------------------------------------------------------------------------------------------------------------- #

# Performs a deep copy of the original data #

# ----------------------------------------------------------------------------------------------------------------- #

    original_spiketimes = deepcopy(spike_data.spiketimes)
    original_spikeshapes = deepcopy(spike_data.spikeshapes)

# ----------------------------------------------------------------------------------------------------------------- #

# Runs the electrophysiological analysis desired #

# ----------------------------------------------------------------------------------------------------------------- #

    print('MEA analysed: ', MEA)

    ISI = spike_data.hist_ISI(MEA)

    # Writes the analysis in a *.txt file #

    f.write('\n')

    f.write('Your MEA ' + MEA + ' has ' + str(len(spike_data.spiketimes.keys())-1) + ' active channels. \n')
#   f.write(' and your MEA ' + str(key) + ' firing rate is ' + str(FR) + '. \n')
    f.write(' ISI array: ' + str(ISI) + '\n')

#    del Burst
    del spike_data

# f.close()
