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
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------------- #

# Second block defines the methods for the calculations #

# ----------------------------------------------------------------------------------------------------------------- #


def electrode_FR(spikedata):

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

# Computes burst counts and profiles according to Dranias, 2015 #

# Bursts were defined as the presence of four spikes in a 100ms with an interval of 50ms to the next spike after #


def burstdranias(spikedata):

    # Variables #

    burstcount = 0  # Overall burst count #
    burstprofile = dict()
    electrodecount = dict()

    spikecount = 0

    initial_pos = 0  # Position on spiketimes array #
    final_pos = 1

    for electrode in spikedata.spiketimes.keys():  # Computing it for all channels #

        if electrode == 'duration':  # First position on the spiketimes dictionary is the duration of the recording #

            continue

        print('Channel analysed: ', electrode)
        burstprofile[electrode] = dict()
        burstevent = 0  # Electrode burst count #

        while final_pos <= len(spikedata.spiketimes[electrode]):  # Keeps the code from running into the arrays limit #

            while spikecount < 4:

                if final_pos >= len(spikedata.spiketimes[electrode])-1:  # Prevents eternal loop #

                    break

                # This is the difference being computed (is it less than 100ms for four spikes?) #

                time_difference = spikedata.spiketimes[electrode][final_pos] - spikedata.spiketimes[electrode][initial_pos]

#                print("Electrode: ", electrode, "Final position:", final_pos)

                if time_difference <= 100:

                    spikecount = spikecount + 1
#                    print("Burst in progress. Total count: ", spikecount, "with a difference of:", time_difference)
                    final_pos = final_pos + 1

                else:

                    spikecount = 0
#                    print("ABORTED with a spike count of: ", spikecount, "and a difference of:", time_difference)
                    initial_pos = final_pos
                    final_pos = final_pos + 1

            # If the burst has more than four spikes keeps adding them until it exhausts the event #

            while time_difference <= 100:

                if final_pos >= len(spikedata.spiketimes[electrode])-1:

                    break

                spikecount = spikecount + 1
                final_pos = final_pos + 1
                time_difference = spikedata.spiketimes[electrode][final_pos] - spikedata.spiketimes[electrode][initial_pos]

            if final_pos >= len(spikedata.spiketimes[electrode])-1:  # Last save when reaches limit #

                break

            # Accounting for interburst interval (IBI) of 50 ms #

            if spikedata.spiketimes[electrode][final_pos + 1] - spikedata.spiketimes[electrode][final_pos] <= 50:

                print('Dictionary created for electrode', electrode)
                burstcount = burstcount + 1
                burstprofile[electrode][burstevent] = list()
#                print('Event number:', burstevent, 'on electrode', electrode, 'has', final_pos, 'positional end.')

                # Saves the bursts separating them by event #

                for n in range(0, spikecount):

                    burstprofile[electrode][burstevent].append(str(spikedata.spiketimes[electrode][final_pos - n]))
#                    print('Adding time', spikedata.spiketimes[electrode][final_pos - n], 'ms.')

                burstevent = burstevent + 1  # Moves to the next burst occurrence

            spikecount = 0
            initial_pos = final_pos + 1
            final_pos = final_pos + 2

            if len(burstprofile[electrode]) != 0:

                electrodecount[electrode] = dict()
                electrodecount[electrode] = len(burstprofile[electrode])  # Computing the counts

    return burstcount, electrodecount, burstprofile

# Methods for data visualisation #


def hist_ISI(spikedata, MEA):

    fig = plt.figure()

    intervals = dict()
    overallISI = list()

    initial_position = 0
    final_position = 1

    for electrode in spikedata.spiketimes.keys():

        if electrode == 'duration':  # First position on the spiketimes dictionary is the duration of the recording #

            continue

        print('Channel analysed: ', electrode, 'with', len(spikedata.spiketimes[electrode]), 'spikes.')
        intervals[electrode] = list()  # Each list stores the ISIs of a given electrode

        while final_position < len(spikedata.spiketimes[electrode]):  # Keeps the code into the arrays limit #

            ISI = spikedata.spiketimes[electrode][final_position] - spikedata.spiketimes[electrode][initial_position]
            intervals[electrode].append(ISI)
            overallISI.append(ISI)
            final_position = final_position + 1
            initial_position = initial_position + 1

    fig.add_subplot()
    plt.hist(overallISI, bins=100, label=MEA)  # Plot per MEA
    plt.legend(loc=1, prop={'size': 8})  # Use for the electrode specific plot
    plt.ylabel('Frequency')
    plt.xticks(np.linspace(0, 7000))
    plt.xlabel('ISIs (ms)')
    plt.show()

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

# file = full_path + "\Debug_Output_exclusionless.txt"
# f = open(file, 'w')
# f.write("Folder analysed: " + full_path)
# f.write(str(datetime.datetime.now().strftime(" | Date: %d-%m-%y Time: %H-%M \n \n")))

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

    hist_ISI(spike_data, MEA)

#    FR = MEA_overall_firingrate()
#    Burst = burstdranias(spike_data)

    # Writes the analysis in a *.txt file #

#    f.write('\n')

#    f.write('Your MEA ' + MEA + ' has ' + str(len(spike_data.spiketimes.keys())-1) + ' active channels. \n')
#    f.write(' and your MEA ' + str(key) + ' firing rate is ' + str(FR) + '. \n')
#    f.write(' Burst profile: ' + str(Burst) + '\n')

#    del Burst
    del spike_data

# f.close()
