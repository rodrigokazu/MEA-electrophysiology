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
import seaborn as sns

# ----------------------------------------------------------------------------------------------------------------- #

# Method definitions #

# ----------------------------------------------------------------------------------------------------------------- #


def folderwide_recursive_spike_detection(MEAs_paths):

    """ Reads a dictionary with paths to electrophysiological recordings from multielectrode arrays exported with the
    MCD_files_export_uV_and_mS_plus_METADATA.m script as *.mat files and runs further analysis

              Arguments:

                  MEAs_paths(dict): Dictionary with paths to the recordings

            Returns:

               SPKS object saved as a *.obj.

              """

    for key in MEAs_paths.keys():

        folder = str(MEAs_paths[key]) + "\\"  # Windows
        #folder = str(MEAs_paths[key]) + "/"  # Unix
        MEA = str(key)

        raw_timeseries = object_constructor(folder, MEA)

        if MEA == "10672" or "10678":

            raw_timeseries = raw_timeseries.exclusion(channel='33')

        raw_timeseries.recursive_spike_detection(MEA=MEA, figpath=folder)


def folderwide_complete_analysis(MEAs_paths):

    for key in MEAs_paths.keys():

        folder = str(MEAs_paths[key]) + "\\"  # Windows
        #folder = str(MEAs_paths[key]) + "/"  # Unix
        MEA = str(key)

        print('Started the complete analysis for MEA', MEA, 'inside folder', folder, 'at',
              time.asctime(time.localtime(time.time())))

        pickle_object = open(folder+MEA+".obj", 'rb')
        SPKS = pickle.load(pickle_object)  # Imports the detected spikes

        filename = MEA + "_number_of_detections_per_electrode"

        SPKS.number_of_detections(filename=filename, output_path=folder)  # Writing the detections

        # Computing and writing FRs #

        filename = MEA + "_firing_rate_per_electrode"

        elec_FR = SPKS.electrode_FR()  # Computing FRs

        dict_to_file(dict=elec_FR, filename=filename, output_path=folder)  # Saving FRs
        FR_perelectrode_barplot(figpath=folder, firingrates=elec_FR, MEA=MEA)  # Plotting FRs

        filename = MEA + "_overall_firing_rate_"

        write_FRs(MEA=MEA, FR=SPKS.MEA_overall_firingrate(), filename=filename, output_path=folder)

        # Burst analysis #

        SPKS.hist_ISI_MEA(figpath=folder, MEA=MEA)  # Plots the inter-spike intervals

        SPKS.burstduration_visualisation(figpath=folder, MEA=MEA)  # Computing for multiple burst definitions

        # Complex Networks #

        filename = MEA + "_CN_analysis"

        SPKS.complete_cn_analysis(filename=filename, output_path=folder)


def MEA_path_acquisition(full_path):

    """ Acquires the paths to electrophysiological recordings from multielectrode arrays exported with the
    MCD_files_export_uV_and_mS_plus_METADATA.m script as *.mat files and runs further analysis

          Arguments:

              full_path(str): Paths to the directory where the recordings are stored in folders with the MEA
              number.

        Returns:

           MEA_paths dictionary with MEA numbers as keys and paths as values.

          """

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


def object_constructor(folder, MEA):  # Initialising the RAW_NeuronalData object and imports data files. #

    """Constructs a RAW_NeuronalData object from a electrophysiological recording from a multielectrode array exported
    with the MCD_files_export_uV_and_mS_plus_METADATA.m script as *.mat file and runs the object through a bandstop (50Hz,
    order 3) and  a high pass filter (20Hz)

          Arguments:

              folder(str): Path to the directory where the recording is stored
              MEA: Number of the MEA recorded

            Returns:

               Filtered RAW_NeuronalData object

              """

    uv_data = folder + MEA + '_RAW_voltage_data.mat'
    time_array = folder + MEA + '_time_array_ms.mat'
    channelids = folder + MEA + '_correct_electrode_order.mat'

    raw_data = RAW_NeuronalData(uv_data=uv_data, time_array=time_array, channelids=channelids, input='MATLAB')

    print('RAW_NeuronalData object for ', MEA, ' created at ', time.asctime(time.localtime(time.time())))  # For profiling

    # Filtering #

    # filtered_data = raw_data.bandstop_resonator()
    # filtered_data = filtered_data.highpass()

    # print('Data filtered (Notch filter with Q = 10, and fs = 50Hz) at', time.asctime(time.localtime(time.time())))

    return raw_data

# ----------------------------------------------------------------------------------------------------------------- #

# Run analysis #

# ----------------------------------------------------------------------------------------------------------------- #


print("\n \n Welcome to the University of Reading - Brain Embodiment Laboratory (SBS - BEL) \n "
      "This module was designed evaluate the firing of recordings from a folder containing *.mat files. \n"
      " You NEED to have the original *.mat files processed with the MCD_files_export_uV_and_mS_plus_METADATA.m script."
      " \n Your *.mat files must be inside folders named with the MEA number, please insert the complete folder path: ")

full_path = input()

MEAs_paths = MEA_path_acquisition(full_path)

folderwide_recursive_spike_detection(MEAs_paths)

#folderwide_complete_analysis(MEAs_paths)