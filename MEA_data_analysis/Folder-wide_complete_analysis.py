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
import os.path
import pandas as pd

# ----------------------------------------------------------------------------------------------------------------- #

# Method definitions #

# ----------------------------------------------------------------------------------------------------------------- #


def defective_electrode_removal(DIV, defective_electrodes, MEA, SPKS):

    for density in defective_electrodes[DIV]:

        for culture in defective_electrodes[DIV][density]:

            if culture == MEA:

                SPKS.exclusion(defective_electrodes[DIV][density][culture])


def folderwide_recursive_spike_detection(MEAs_paths):

    """ Reads a dictionary with paths to electrophysiological recordings from multielectrode arrays exported with the
    MCD_files_export_uV_and_mS_plus_METADATA.m script as *.mat files and runs further analysis

              Arguments:

                  MEAs_paths(dict): Dictionary with paths to the recordings

            Returns:

               SPKS object saved as a *.obj.

              """

    for key in MEAs_paths.keys():

        #folder = str(MEAs_paths[key]) + "\\"  # Windows
        folder = str(MEAs_paths[key]) + "/"  # Unix
        MEA = str(key)

        raw_timeseries = RAW_object_constructor(folder, MEA)

        if MEA == "10672" or "10678":

            raw_timeseries = raw_timeseries.exclusion(channel='33')

        raw_timeseries.recursive_spike_detection(MEA=MEA, figpath=folder)

        del raw_timeseries
        gc.collect()


def folderwide_complete_analysis(MEAs_paths, output_path):

    folder_metrics = dict()

    MEA_detections = 0
    overall_firingrate = 0
    overall_activeelectrodes = 0
    burstcount = 0
    active_electrodes = 0
    overallISI = 0
    DIV_ISI = list()

    folder_metrics["MEAs"] = list()
    folder_metrics["Individual_detections"] = list()
    folder_metrics["Individual_FRs"] = list()
    folder_metrics["Individual_Burst_Counts"] = list()
    folder_metrics["Individual_Active_Elecs"] = list()
    folder_metrics["Individual_ISI"] = list()

    for key in MEAs_paths.keys():

        folder = str(MEAs_paths[key]) + "\\"  # Windows
        #folder = str(MEAs_paths[key]) + "/"  # Unix
        MEA = str(key)
        DIV = 'DIV7'  # DIV to be analysed

        folder_metrics["MEAs"].append(MEA)

        print('Started the complete analysis for MEA', MEA, 'inside folder', folder, 'at',
              time.asctime(time.localtime(time.time())))

        pickle_object = open(folder+MEA+".obj", 'rb')
        SPKS = pickle.load(pickle_object)  # Imports the detected spikes

        # Removing defective electrodes

        defective_electrode_removal(DIV=DIV, defective_electrodes=defective_electrodes, MEA=MEA, SPKS=SPKS)

        MEA_active_elecs = SPKS.active_electrodes()

        SPKS.visualise_rasters(figpath=output_path, MEA=MEA)  # Raster plot of detections

        folder_metrics["Individual_Active_Elecs"].append(MEA_active_elecs)

        overall_activeelectrodes = overall_activeelectrodes + MEA_active_elecs

        filename = MEA + "_number_of_detections_per_electrode"

        Individual_detection = SPKS.number_of_detections(filename=filename, output_path=folder)

        folder_metrics["Individual_detections"].append(Individual_detection)

        MEA_detections = MEA_detections + Individual_detection   # Writing the detections

        # Computing and writing FRs #

        filename = MEA + "_firing_rate_per_electrode"

        elec_FR = SPKS.electrode_FR()  # Computing FRs

        dict_to_file(dict=elec_FR, filename=filename, output_path=folder)  # Saving FRs
        FR_perelectrode_barplot(figpath=folder, firingrates=elec_FR, MEA=MEA)  # Plotting FRs

        SPKS.visualise_rasters(figpath=output_path, MEA=MEA)  # Raster plot of detections

        filename = MEA + "_overall_firing_rate_"

        MEA_FR = SPKS.MEA_overall_firingrate()

        folder_metrics["Individual_FRs"].append(MEA_FR)

        overall_firingrate = MEA_FR + overall_firingrate

        write_FRs(MEA=MEA, FR=overall_firingrate, filename=filename, output_path=folder)

        # Burst analysis #

        MEA_ISI = SPKS.hist_ISI_MEA(figpath=folder, MEA=MEA)  # Plots the inter-spike intervals

        DIV_ISI.extend(MEA_ISI[0]) # Computes the average ISI for that DIV

        folder_metrics["Individual_ISI"].append(MEA_ISI)

        if np.isnan(overallISI) == True:

            overallISI = 0

        overallISI = overallISI + MEA_ISI[1]

        MEA_burst = SPKS.burstdranias_500ms(MEA=MEA)

        folder_metrics["Individual_Burst_Counts"].append(MEA_burst)

        #burstcount = MEA_burst + burstcount
        #SPKS.burstduration_visualisation(figpath=folder, MEA=MEA)  # Computing for multiple burst definitions

        # Complex Networks #

        filename = MEA + "_CN_analysis"

        SPKS.complete_cn_analysis(filename=filename, output_path=folder, MEA=MEA)

    DIV_ISI_histogram(filename="RAW", DIV=DIV, figpath=output_path, ISIlist=DIV_ISI) # Plots the average ISIs for that DIV as a histogram to educate CN analysis

    number_of_cultures = len(MEAs_paths.keys())

    folder_metrics["Average_detections"] = MEA_detections/number_of_cultures
    folder_metrics["Average_FR"] = overall_firingrate/number_of_cultures
    folder_metrics["Average_Burst_Count"] = burstcount/number_of_cultures
    folder_metrics["Average_Active_Channels"] = overall_activeelectrodes/number_of_cultures
    folder_metrics["Average_ISI"] = overallISI/number_of_cultures

    dataframe = pd.DataFrame(folder_metrics)

    filename = "DIV_Analysis_Output"

    dataframe.to_excel(output_path+filename+'.xlsx')
    dict_to_file(dict=folder_metrics, filename=filename, output_path=output_path)  # Saving DIV metrics


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


def MC_detected_ephys_analysis(MEAs_paths, output_path):

    folder_metrics = dict()

    MEA_detections = 0
    overall_firingrate = 0
    overall_activeelectrodes = 0
    burstcount = 0
    active_electrodes = 0
    overallISI = 0
    DIV_ISI = list()

    folder_metrics["MEAs"] = list()
    folder_metrics["Individual_detections"] = list()
    folder_metrics["Individual_FRs"] = list()
    folder_metrics["Individual_Burst_Counts"] = list()
    folder_metrics["Individual_Active_Elecs"] = list()
    folder_metrics["Individual_ISI"] = list()

    for key in MEAs_paths.keys():

        folder = str(MEAs_paths[key]) + "\\"  # Windows
        # folder = str(MEAs_paths[key]) + "/"  # Unix
        MEA = str(key)
        DIV = 'DIV7'  # DIV to be analysed

        print('Started the complete analysis for MEA', MEA, 'inside folder', folder, 'at',
              time.asctime(time.localtime(time.time())))

        SPKS = SPKS_object_constructor(folder=folder, MEA=MEA)  # Imports the detected spikes

        if SPKS == 0:

            continue

        folder_metrics["MEAs"].append(MEA)

        # Removing defective electrodes

        defective_electrode_removal(DIV=DIV, defective_electrodes=defective_electrodes, MEA=MEA, SPKS=SPKS)

        MEA_active_elecs = SPKS.active_electrodes()  # How many electrodes were active

        SPKS.visualise_rasters(figpath=output_path, MEA=MEA)  # Raster plot of detections

        folder_metrics["Individual_Active_Elecs"].append(MEA_active_elecs)  # How many electrodes were active

        overall_activeelectrodes = overall_activeelectrodes + MEA_active_elecs  # How many electrodes were active

        filename = MEA + "MC_number_of_detections_per_electrode"

        Individual_detection = SPKS.number_of_detections(filename=filename, output_path=folder)  # How many SPIKES

        folder_metrics["Individual_detections"].append(Individual_detection)

        MEA_detections = MEA_detections + Individual_detection  # Writing the detections

        # Computing and writing FRs #

        filename = MEA + "MC_firing_rate_per_electrode"

        elec_FR = SPKS.electrode_FR()  # Computing FRs

        dict_to_file(dict=elec_FR, filename=filename, output_path=folder)  # Saving FRs
        FR_perelectrode_barplot(figpath=folder, firingrates=elec_FR, MEA=MEA)  # Plotting FRs

        SPKS.visualise_rasters(figpath=output_path, MEA=MEA)  # Raster plot of detections

        filename = MEA + "MC_overall_firing_rate_"

        MEA_FR = SPKS.MEA_overall_firingrate()

        folder_metrics["Individual_FRs"].append(MEA_FR)

        overall_firingrate = MEA_FR + overall_firingrate

        write_FRs(MEA=MEA, FR=overall_firingrate, filename=filename, output_path=folder)

        # Burst analysis #

        MEA_ISI = SPKS.hist_ISI_MEA(figpath=folder, MEA=MEA)  # Plots the inter-spike intervals

        DIV_ISI.extend(MEA_ISI[0])  # Computes the average ISI for that DIV

        folder_metrics["Individual_ISI"].append(MEA_ISI)

        if np.isnan(overallISI) == True:

            overallISI = 0

        overallISI = overallISI + MEA_ISI[1]

        MEA_burst = SPKS.burstdranias_500ms(MEA=MEA)

        folder_metrics["Individual_Burst_Counts"].append(MEA_burst)

        # burstcount = MEA_burst + burstcount
        # SPKS.burstduration_visualisation(figpath=folder, MEA=MEA)  # Computing for multiple burst definitions

        # Complex Networks #

        filename = MEA + "MC_CN_analysis"

        SPKS.complete_cn_analysis(filename=filename, output_path=folder, MEA=MEA)

    DIV_ISI_histogram(filename="MC", DIV=DIV, figpath=output_path,
                      ISIlist=DIV_ISI)  # Plots the average ISIs for that DIV as a histogram to educate CN analysis

    number_of_cultures = len(MEAs_paths.keys())

    folder_metrics["Average_detections"] = MEA_detections / number_of_cultures
    folder_metrics["Average_FR"] = overall_firingrate / number_of_cultures
    folder_metrics["Average_Burst_Count"] = burstcount / number_of_cultures
    folder_metrics["Average_Active_Channels"] = overall_activeelectrodes / number_of_cultures
    folder_metrics["Average_ISI"] = overallISI / number_of_cultures

    dataframe = pd.DataFrame(folder_metrics)

    filename = "MC_DIV_Analysis_Output"

    dataframe.to_excel(output_path + filename + '.xlsx')
    dict_to_file(dict=folder_metrics, filename=filename, output_path=output_path)  # Saving DIV metrics

    return 0


def RAW_object_constructor(folder, MEA):  # Initialising the RAW_NeuronalData object and imports data files. #

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
    uv_data_2 = folder + MEA + '_RAW_voltage_data_2.mat'

    print('Started analysis for ', MEA, ' at ',
          time.asctime(time.localtime(time.time())), '. \nCreating RAW_NeuronalData object, please stand by...' )

    raw_data = RAW_NeuronalData(uv_data=uv_data, time_array=time_array, channelids=channelids, input='MATLAB')

    print('RAW_NeuronalData object for ', MEA, ' created at ', time.asctime(time.localtime(time.time())))  # For profiling

    # Filtering #

    # filtered_data = raw_data.bandstop_resonator()
    # filtered_data = filtered_data.highpass()

    # print('Data filtered (Notch filter with Q = 10, and fs = 50Hz) at', time.asctime(time.localtime(time.time())))

    return raw_data


def SPKS_object_constructor(folder, MEA):  # Initialising the RAW_NeuronalData object and imports data files. #

    """Constructs a SPKS_NeuronalData object from a electrophysiological recording from a multielectrode array exported
    with the MCD_files_export_uV_and_mS_plus_METADATA.m script as *.mat file and runs the object through a bandstop (50Hz,
    order 3) and  a high pass filter (20Hz)

          Arguments:

              folder(str): Path to the directory where the recording is stored
              MEA: Number of the MEA recorded



            Returns:

                   Filtered SPKS_NeuronalData object

              """

    time_array = folder + MEA + '_time_array_ms.mat'
    channelids = folder + MEA + '_correct_electrode_order.mat'
    occurrence_ms = folder + MEA + '_spiketimes_ms.mat'
    shapedata = folder + MEA + '_spikevalues_uV.mat'

    if os.path.exists(shapedata) is True:

        print('Started analysis for ', MEA, ' at ',
              time.asctime(time.localtime(time.time())), '. \nCreating SPKS_NeuronalData object, please stand by...' )

        SPKS = SPKS_NeuronalData(time_array=time_array, channelids=channelids, occurrence_ms=occurrence_ms,
                                 shapedata=shapedata, input='MATLAB')

        # For profiling #

        print('SPKS_NeuronalData object for ', MEA, ' created at ', time.asctime(time.localtime(time.time())))

        # Filtering #

        # filtered_data = raw_data.bandstop_resonator()
        # filtered_data = filtered_data.highpass()

        # print('Data filtered (Notch filter with Q = 10, and fs = 50Hz) at', time.asctime(time.localtime(time.time())))

        return SPKS

    else:

        print('No Spikes saved for MEA ', MEA)

        return 0

# ----------------------------------------------------------------------------------------------------------------- #

# Defective electrodes #

# ----------------------------------------------------------------------------------------------------------------- #


defective_electrodes = {"DIV7": {"Low_density": {"7501": [33, 74, 84, 75, 85],
                                                 "7610": [61, 71, 62, 72, 33, 53, 73, 24, 65],
                                                 "7611": [31, 41, 61, 44, 64],
                                                 "7612": [47, 55, 56, 57, 58],
                                                 "7616": [31, 41, 61, 71, 42, 52, 62, 72, 44, 54],
                                                 "7641": [33],
                                                 "10663": [33],
                                                 "10671": [33],
                                                 "10674": [33],
                                                 "10681": [33, 73]},

                                 "Mid_density": {"7558": [33],
                                                 "7615": [33],
                                                 "10672": [33],
                                                 "10679": [],
                                                 "10688": []},

                                 "High_density": {"7614": [33, 43, 25, 35, 27, 37],
                                                  "7620": [26, 33, 36],
                                                  "10682": [13, 24, 31, 54, 61, 65, 67, 75, 87],
                                                  "10683": [33]}},

                        "DIV14": {"Low_density": {"7610": [33],
                                                  "7611": [21, 22, 33],
                                                  "7612": [33],
                                                  "10663": [33],
                                                  "10671": [33]},

                                  "Mid_density": {"7558": [64],
                                                  "7555": [33],
                                                  "10672": [33, 43]},

                                  "High_density": {"7614": [12, 22, 25, 33, 53, 64],
                                                   "7620": [33, 36, 61, 62],
                                                   "10678": [33],
                                                   "10682": [33]}},

                        "DIV21": {"Low_density": {"7612": [33, 38],
                                                  "10663": [33, 38, 48, 71],
                                                  "10671": [33, 42]},

                                  "Mid_density": {"7558": [33],
                                                  "10672": [33]},

                                  "High_density": {"7614": [27, 33, 37, 65],
                                                   "7620": [33]}},

                        "DIV28": {"Low_density": {"7612": [28, 33]},

                                  "Mid_density": {"7558": [14, 32, 33, 46],
                                        "10672": [14, 33, 34, 35, 45]},

                                  "High_density": {"7614": [27, 33, 37, 65]}}
                        }


# ----------------------------------------------------------------------------------------------------------------- #

# Run analysis #

# ----------------------------------------------------------------------------------------------------------------- #


print("\n \n Welcome to the University of Reading - Brain Embodiment Laboratory (SBS - BEL) \n "
      "This module was designed evaluate the firing of recordings from a folder containing *.mat files. \n"
      " You NEED to have the original *.mat files processed with the MCD_files_export_uV_and_mS_plus_METADATA.m script."
      " \n Your *.mat files must be inside folders named with the MEA number, please insert the complete folder path: ")

full_path = input()

MEAs_paths = MEA_path_acquisition(full_path)

MC_detected_ephys_analysis(MEAs_paths=MEAs_paths, output_path=full_path)

folderwide_recursive_spike_detection(MEAs_paths)

folderwide_complete_analysis(MEAs_paths=MEAs_paths, output_path=full_path)