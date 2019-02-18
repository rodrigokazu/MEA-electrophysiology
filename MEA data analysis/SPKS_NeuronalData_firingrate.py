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


import datetime
from pathlib import Path
from copy import deepcopy
from class_SPKS_NeuronalData import SPKS_NeuronalData


# ----------------------------------------------------------------------------------------------------------------- #

# loadmat will import your *.mat datafile as a dictionary, PASTE YOUR FOLDER HERE. #

# ----------------------------------------------------------------------------------------------------------------- #

# OLD ADVICE - JULY 2018 -- NOT NEEDED! #

# Useful advice: Problem is with the string. Here, \U starts an eight-character Unicode escape, such as '\U00014321`. #
# In your code, the escape is followed by the character 's', which is invalid. #
# Duplicate all the backslashes #

# ----------------------------------------------------------------------------------------------------------------- #

print("\n \n Welcome to the University of Reading - Brain Embodiment Laboratory (SBS - BEL) \n \n \n This script was designed compute the firing rate of recordings from a folder containing *.mat files. \n \n \n You NEED to have the original *.mat files processed with the MCD_files_export_uV_and_mS_plus_METADATA.m script \n \n \n  Your *.mat files must be inside folders named with the MEA number \n \n \n")

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

f = open('.\..\Analysis_Output.txt', 'w')    # Writes the analysis into a *.txt file #
f.write('\n \n')
f.write(full_path)

for key in MEAs_paths.keys():

    folder = str(MEAs_paths[key]) + '\\'
    MEA = str(key)

# ----------------------------------------------------------------------------------------------------------------- #

# Second Block #

# Initialises the object of NeuronalData and imports the data files. #

# ----------------------------------------------------------------------------------------------------------------- #

    shapedata = folder + MEA + '_spikevalues_uV.mat'
    time_array = folder + MEA + '_time_array_ms.mat'
    channelids = folder + MEA + '_correct_electrode_order.mat'
    occurrence_ms = folder + MEA + '_spiketimes_ms.mat'

    spikedata = SPKS_NeuronalData(shapedata,time_array, occurrence_ms, channelids)

# ----------------------------------------------------------------------------------------------------------------- #

# Copying the data #

# ----------------------------------------------------------------------------------------------------------------- #

    original_spiketimes = deepcopy(spikedata.spiketimes)
    original_spikeshapes = deepcopy(spikedata.spikeshapes)

# ----------------------------------------------------------------------------------------------------------------- #

    def electrode_FR():

        firingrates = {}

        # Compute the record duration to seconds from ms #

        duration_ms = spikedata.spiketimes['duration']
        duration_s = duration_ms/1000

        for key in spikedata.spikeshapes:

            # Compute the total spike number per electrode #

            spike_number = len(spikedata.spikeshapes[key])

            # Compute and store the firing rates #

            electrode_fr_s = spike_number/duration_s
            firingrates[key] = electrode_fr_s

#            print('Electrode', key, 'has a firing rate of', electrode_fr_s)

        return firingrates

    def MEA_overall_firingrate():

        individual_fr = electrode_FR()
        spikecount = 0

        for key in individual_fr:

            spikecount = individual_fr[key] + spikecount

        overall_firingrate_s = spikecount/60

        return overall_firingrate_s


    FR = MEA_overall_firingrate()

    # Writes the analysis in a *.txt file #

    f.write('\n \n')

    f.write(str(datetime.datetime.now().strftime("Date: %d-%m-%y Time: %H-%M")))
    f.write(' Your MEA ' + str(key) + ' has ' + str(len(spikedata.spikeshapes.keys())) + ' active channels')
    f.write(' and your MEA ' + str(key) + ' firing rate is ' + str(FR))

f.close()