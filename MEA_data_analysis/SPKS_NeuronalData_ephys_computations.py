# Brain Embodiment Laboratory #
# University of Reading #

# -----------------------------------------------------------------------------------------------------------------#

# BEL's Script to compute firing rates of cultured neuronal networks as MCD files#
# Use after the files were treated with the MCD_files_export_uV_and_mS_plus_METADATA script provided#

# ----------------------------------------------------------------------------------------------------------------- #

# Written by Rodrigo Kazu #
# Any enquiries to r.siqueiradesouza@sheffield.ac.uk #

# ----------------------------------------------------------------------------------------------------------------- #

# First block import the relevant libraries and initialises the important variables #

# ----------------------------------------------------------------------------------------------------------------- #

from class_SPKS_NeuronalData import SPKS_NeuronalData
from copy import deepcopy
import datetime
import matplotlib.cbook
import matplotlib.pyplot as plt
from pathlib import Path
import warnings

# Methods for data visualisation first #

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)  # Ignores pointless matplotlib warnings
plt.rcParams.update({'font.size': 10})


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


# File handling #

# file = full_path + "\Debug_Output_IBI_500ms.txt"
# f = open(file, 'w')
#nf.write("Folder analysed: " + full_path)
# f.write(str(datetime.datetime.now().strftime(" | Date: %d-%m-%y Time: %H-%M \n ")))

# Figure and plot handling #

# fig = plt.figure(dpi=300)  # Creates a figure for data visualisation #
# plotnumber = 1

# Loops through MEAs #

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

# ----------------------------------------------------------------------------------------------------------------- #

# Performs a deep copy of the original data #

# ----------------------------------------------------------------------------------------------------------------- #

    original_spiketimes = deepcopy(spike_data.spiketimes)
    original_spikeshapes = deepcopy(spike_data.spikeshapes)

# ----------------------------------------------------------------------------------------------------------------- #

# Runs the electrophysiological analysis desired #

# ----------------------------------------------------------------------------------------------------------------- #

    print('MEA analysed: ', MEA)

    spike_data.hist_ISI_MEA(MEA)

#    fig.add_subplot(1, 2, plotnumber)

#    plotnumber = plotnumber + 1

    # Writes the analysis in a *.txt file #

#    f.write('\n')

#    f.write('Your MEA ' + MEA + ' has ' + str(len(spike_data.spiketimes.keys())-1) + ' active channels. \n\n')
#   f.write(' and your MEA ' + str(key) + ' firing rate is ' + str(FR) + '. \n')
#    f.write('Burst count per electrode: ' + str(spike_data.burstdranias_100ms(MEA)) + '\n')


# f.close()