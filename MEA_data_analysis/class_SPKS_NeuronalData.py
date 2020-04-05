import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import scipy.signal as signal
import scipy.io
from class_RAW_NeuronalData import *

#warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)  # Ignores pointless matplotlib warnings
#plt.switch_backend('agg')
plt.rcParams.update({'font.size': 5})


class SPKS_NeuronalData:

    def __init__(self, input, occurrence_ms, shapedata, **args):

        """ Reads multiple *.mat files with empirically recorded neuronal data from multielectrode arrays exported with
        MCD_files_export_uV_and_mS_plus_METADATA.m script contained pre-detected spike trains and generates a
        SPKS_NeuronalData object. Alternatively, imports the same information from the recursive spike detection of the
        class RAW_NeuronalData

               Arguments:

                   input (str): Either "RAWdata" or "MATLAB" as the source of the data
                   occurrence_ms(str or dict): path to the *.mat file containing the spike times or dictionary with
                   spiketimes if the source is "RAWdata".
                   shapedata(str or dict): path to the *.mat file containing the spike shapes or dictionary with
                   spikeshapes if the source is "RAWdata".
                   duration(int): Record duration is the source is "RAWdata"
                   time_array (str): path to the *.mat file containing the recorded timestamps in ms (MATLAB only)
                   channelids (str): path to the *.mat file containing the recorded electrode numbers (MATLAB only)

               Returns:

                  SPKS_NeuronalData object
               """
        # MATLAB input needs the extra arguments time_array and channelids #

        self.spiketimes = {}
        self.spikeshapes = {}

        # Imports data #

        if input == "MATLAB":

            recorded_timedata = scipy.io.loadmat(args.pop('time_array'))
            recorded_channelids = scipy.io.loadmat(args.pop('channelids'))
            input_occurrencedata = scipy.io.loadmat(occurrence_ms)
            input_shapedata = scipy.io.loadmat(shapedata)

            # The first index after it stands for the matrix line, the second one for the column #
            # Column ZERO has all the channel names, already in the correct order #

            record_duration = len(recorded_timedata['timedata'][0])

            self.spiketimes['duration'] = record_duration  # First entry of the dictionary will be the time in ms #

            for channel in range(0, 60):

                key = recorded_channelids['channelID_matrix'][channel][0][0]  # First column has the channel IDs #

                spike_number = len(input_occurrencedata['spiketimes'][0:60][channel][0])

                if spike_number > 4:  # Channels with less than or 4 spikes are excluded from further analysis #

                    # Stores the Spike Shapes #

                    self.spikeshapes[key] = list()
                    transpose = np.transpose(input_shapedata['spikedata_cell'][0:60][channel][0])
                    self.spikeshapes[key] = transpose

                    # Fills the arrays with the times of spikes in ms #

                    self.spiketimes[key] = list()

                    for spike_event in range(0, spike_number):

                        self.spiketimes[key].append(input_occurrencedata['spiketimes'][0:60][channel][0][spike_event][0])

        elif input == "RAWdata":

            for channel in occurrence_ms.keys():

                # Channels with less than or 4 spikes are excluded from further analysis #

                if len(occurrence_ms[channel]) >= 4:

                    self.spiketimes[channel] = occurrence_ms[channel]

            self.spiketimes['duration'] = args.pop('duration')

            for channel in self.spiketimes.keys():

                if channel != 'duration':

                    if len(occurrence_ms[channel]) >= 4:

                        self.spikeshapes[channel] = shapedata[channel]

    def exclusion(self):

        """ Remove electrodes from the RAW_NeuronalData object

            Arguments:

                SPKS_NeuronalData object

            Returns:

               Updated SPKS_NeuronalData object
            """

        print("Please enter one channel to be excluded (enter zero to skip to the next MEA recording) from: \n ", self.spiketimes.keys())

        channel = input()

        while channel != '0':

            del self.spiketimes[str(channel)]
            del self.spikeshapes[str(channel)]
            channel = input()

# ----------------------------------------------------------------------------------------------------------------- #

# Methods for electrophysiological calculations #

# ----------------------------------------------------------------------------------------------------------------- #

    def bin_the_spikes(self, bin_count):

        bin_count = int(bin_count)

        binned_channels = {}  # Dictionary that will store the binned arrays

        for keys in self.spiketimes.keys():

            if keys != 'duration':

                if keys != 'mock_spiketimes':

                    binned_channels[keys] = np.empty(bin_count)  # Adds zero to each position of the binned array

                    for binning in range(0, len(self.spiketimes[keys])):

                        for bin_comparison in range(1, bin_count):

                            current_bin = bin_comparison * 25000
                            last_bin = current_bin - 25000

                            if last_bin < self.spiketimes[keys][binning] < current_bin:

                                binned_channels[keys][bin_comparison] = binned_channels[keys][bin_comparison] + 1

        return binned_channels

    def electrode_FR(self):

        """ Computes the firing rates in Hz for all electrodes of a SPKS_NeuronalData object

            Arguments:

                SPKS_NeuronalData object

            Returns:

               Dictionary with Firing Rates

            """

        firingrates = {}

        # Compute the record duration to seconds from ms #

        duration_ms = self.spiketimes['duration']
        duration_s = duration_ms / 25000

        for key in self.spiketimes.keys():

            if key != 'duration':

                if key != 'mock_spiketimes':

                    # Compute the total spike number per electrode

                    spike_number = len(self.spiketimes[key])

                    # Compute and store the firing rates #

                    electrode_fr_s = spike_number / duration_s
                    firingrates[key] = electrode_fr_s

        return firingrates

    def MEA_overall_firingrate(self):

        """Computes the firing rates in Hz for a whole SPKS_NeuronalData object (MEA recording)

            Arguments:

                SPKS_NeuronalData object

            Returns:

               Firing rate value in Hz

            """

        individual_fr = self.electrode_FR()
        spikecount = 0

        for key in individual_fr:

            spikecount = individual_fr[key] + spikecount

        if len(self.spiketimes.keys()) > 1:

            active = len(self.spiketimes.keys()) - 1

            overall_firingrate_s = spikecount / active

        else:

            overall_firingrate_s = 0

        return overall_firingrate_s

    def number_of_detections(self, filename, output_path):

        fullname = output_path + filename + ".txt"
        file = open(fullname, "w+")
        all_detections = 0

        for key in self.spiketimes.keys():

            if key != 'duration':

                # Compute the total spike number per electrode #

                spike_number = len(self.spiketimes[key])
                electrode_detections = "Electrode " + str(key) + " had " + str(spike_number) + " detections. \n"
                file.write(str(electrode_detections))
                all_detections = all_detections + spike_number

        overall_detections = "This MEA had " + str(all_detections) + " spikes."
        file.write(str(overall_detections))

        file.close()

        return all_detections

    def burstdranias_100ms(self, MEA):

        """Computes burst counts and profiles of a SPKS_NeuronalData object according to Dranias et al, 2015.
        Bursts were defined as the presence of four spikes in a 100ms with an interval of 50ms to the next spike after.

            Arguments:

                SPKS_NeuronalData object

            Returns:

               Dictionary of bursts per electrode.

            """

        # Variables #

        burstcount = 0  # Overall burst count #
        burstprofile = dict()
        electrodecount = dict()
        burstduration = dict()

        spikecount = 0

        initial_pos = 0  # Position on spiketimes array #
        final_pos = 1

        overallIBI = dict()

        for electrode in self.spiketimes.keys():  # Computing it for all channels #

            if electrode == 'duration':  # First position on the spiketimes dictionary is the duration of recording #

                continue

            print('Channel analysed: ', electrode)

            burstprofile[electrode] = dict()
            burstduration[electrode] = dict()
            overallIBI[electrode] = list()

            burstevent = 0  # Electrode burst count #

            while final_pos <= len(self.spiketimes[electrode]):  # Keeps the code from running into the arrays limit #

                while spikecount < 4:

                    if final_pos >= len(self.spiketimes[electrode]) - 1:  # Prevents eternal loop #

                        break

                    # This is the difference being computed (is it less than 100ms for four spikes?) #

                    time_difference = self.spiketimes[electrode][final_pos] - self.spiketimes[electrode][initial_pos]

                    if time_difference <= 100:

                        spikecount = spikecount + 1
                        final_pos = final_pos + 1

                    else:

                        spikecount = 0
                        initial_pos = final_pos
                        final_pos = final_pos + 1

                # If the burst has more than four spikes keeps adding them until it exhausts the event #

                while time_difference <= 100:

                    if final_pos >= len(self.spiketimes[electrode]) - 1:

                        break

                    spikecount = spikecount + 1
                    final_pos = final_pos + 1
                    time_difference = self.spiketimes[electrode][final_pos] - self.spiketimes[electrode][initial_pos]

                if final_pos >= len(self.spiketimes[electrode]) - 1:  # Last save when reaches limit #

                    break

                # Accounting for interburst interval (IBI) of 50 ms #

                if self.spiketimes[electrode][final_pos + 1] - self.spiketimes[electrode][final_pos] >= 50:

                    overallIBI[electrode].append(self.spiketimes[electrode][final_pos + 1] - self.spiketimes[electrode][final_pos])
                    burstcount = burstcount + 1
                    burstprofile[electrode][burstevent] = list()
                    burstduration[electrode][burstevent] = spikecount

                    # Saves the bursts separating them by event #

                    for n in range(0, spikecount):

                        burstprofile[electrode][burstevent].append(str(self.spiketimes[electrode][final_pos - n]))

                    burstevent = burstevent + 1  # Moves to the next burst occurrence

                spikecount = 0
                initial_pos = final_pos + 1
                final_pos = final_pos + 2

                if len(burstprofile[electrode]) != 0:

                    electrodecount[electrode] = dict()
                    electrodecount[electrode] = len(burstprofile[electrode])  # Computing the counts

        #ax = sns.distplot(burstprofile[electrode], color='y')
        #ax.set(title='MEA ' + MEA)

        return electrodecount

    def burstdranias_500ms(self, MEA):

        """Computes burst counts and profiles of a SPKS_NeuronalData object according to Dranias et al, 2015.
        Bursts were defined as the presence of four spikes in a 500ms based on the timescales of my dataset recorded at
        the  Brain Embodiment Laboratory at the University Of Reading

            Arguments:

                SPKS_NeuronalData object

            Returns:

               Dictionary of bursts per electrode.

            """

        # Variables #

        burstcount = 0  # Overall burst count #
        burstprofile = dict()
        burstduration = dict()
        electrodecount = dict()

        spikecount = 0

        initial_pos = 0  # Position on spiketimes array #
        final_pos = 1

        overallIBI = list()

        for electrode in self.spiketimes.keys():  # Computing it for all channels #

            if electrode == 'duration':  # First position on the spiketimes dictionary is the duration of recording #

                continue

            print('Channel analysed: ', electrode)
            burstprofile[electrode] = dict()
            burstduration[electrode] = dict()

            burstevent = 0  # Electrode burst count #

            while final_pos <= len(self.spiketimes[electrode]):  # Keeps the code from running into the arrays limit #

                while spikecount < 4:

                    if final_pos >= len(self.spiketimes[electrode]) - 1:  # Prevents eternal loop #

                        break

                    # This is the difference being computed (is it less than 100ms for four spikes?) #

                    time_difference = self.spiketimes[electrode][final_pos] - self.spiketimes[electrode][initial_pos]

                    if time_difference <= 500:

                        spikecount = spikecount + 1
                        final_pos = final_pos + 1

                    else:

                        spikecount = 0
                        initial_pos = final_pos
                        final_pos = final_pos + 1

                # If the burst has more than four spikes keeps adding them until it exhausts the event #

                while time_difference <= 500:

                    if final_pos >= len(self.spiketimes[electrode]) - 1:

                        break

                    spikecount = spikecount + 1
                    final_pos = final_pos + 1
                    time_difference = self.spiketimes[electrode][final_pos] - self.spiketimes[electrode][initial_pos]

                if final_pos >= len(self.spiketimes[electrode]) - 1:  # Last save when reaches limit #

                    break

                if self.spiketimes[electrode][final_pos + 1] - self.spiketimes[electrode][final_pos] <= 50:

                    overallIBI.append(self.spiketimes[electrode][final_pos + 1] - self.spiketimes[electrode][final_pos])
                    burstcount = burstcount + 1
                    burstprofile[electrode][burstevent] = list()
                    burstduration[electrode][burstevent] = spikecount

                    # Saves the bursts separating them by event #

                    for n in range(0, spikecount):

                        burstprofile[electrode][burstevent].append(str(self.spiketimes[electrode][final_pos - n]))

                    burstevent = burstevent + 1  # Moves to the next burst occurrence

                spikecount = 0
                initial_pos = final_pos + 1
                final_pos = final_pos + 2

                if len(burstprofile[electrode]) != 0:

                    electrodecount[electrode] = dict()
                    electrodecount[electrode] = len(burstprofile[electrode])  # Computing the counts

        return burstcount

    def get_bin_number(self):

        # Each bin has one second

        duration_ms = self.spiketimes['duration']
        bins = duration_ms / 25000

        return bins

    def cn_xcov_analysis(self, G, binned_channels, filename, output_path):

        dict_xcov_peak_and_threshold_eachpair = dict()

        electrodes = list()

        for keys in self.spiketimes.keys():

            if keys != 'duration':

                electrodes.append(keys)

        for xcov in range(0, len(electrodes)):

            key = electrodes[xcov]

            if key != 'duration':

                first_array = binned_channels[key]
                first_array_centered = first_array - first_array.mean()  # Centers the array

                for xcov_2 in range(xcov + 1, len(electrodes)):

                    if xcov_2 == len(electrodes):

                       continue

                    else:

                        key_2 = electrodes[xcov_2]

                        if key_2 != 'duration':

                            second_array = binned_channels[key_2]

                            second_array_centered = second_array - second_array.mean()  # Centers the array

                            print(' \n\n Correlating channel ', key, 'with channel', key_2, '.')

                            crosscovariance_pair = signal.correlate(first_array_centered, second_array_centered)

                            threshold = 4 * np.mean(crosscovariance_pair)

                            if np.amax(crosscovariance_pair) > threshold: # This finds peaks (Downes 2012)

                                print('Channel pair has a peak of ', np.amax(crosscovariance_pair), " edge added.")

                                G.add_edge(int(key), int(key_2))

                        key = str(key)  # Converts keys into strings for writing
                        key_2 = str(key_2)

                        xcov_key = key + '_' + key_2  # Create a node pair string

                        dict_xcov_peak_and_threshold_eachpair[xcov_key] = \
                            ['Peak:', np.amax(crosscovariance_pair),
                             'Threshold:', threshold]

                        dict_to_file(dict=dict_xcov_peak_and_threshold_eachpair, filename=filename,
                                     output_path=output_path)
        return G

    def complete_cn_analysis(self, filename, output_path):

        G = generateMEA()

        bin_count = self.get_bin_number()

        binned_channels = self.bin_the_spikes(bin_count)

        output_path = output_path

        filename = filename

        G = self.cn_xcov_analysis(G=G, binned_channels=binned_channels, filename=filename, output_path=output_path)

        draw_and_save_graph(G=G, output_path=output_path, filename=filename)

    def active_electrodes(self):

        # Data has to come from RAW_NeuronalData. If MATLAB, subtract one instead.

        active = len(self.spiketimes.keys()) - 1

        return active

# ----------------------------------------------------------------------------------------------------------------- #

# Methods for CN analysis #

# ----------------------------------------------------------------------------------------------------------------- #

# ----------------------------------------------------------------------------------------------------------------- #

# Methods for data visualisation #

# ----------------------------------------------------------------------------------------------------------------- #

    def burstduration_visualisation(self, figpath, MEA):

        """ Barplot of the burst duration of a SPKS_NeuronalData object with 100ms or 500ms definition

              Arguments:

                  SPKS_NeuronalData object
                  MEA(str): MEA number for plot title

              Returns:

                 Barplot.
              """

        Burstduration = self.burstdranias_100ms(MEA)
        dict_to_file(dict=Burstduration, filename=str(MEA)+"burstdranias_100ms", output_path=figpath)

        if len(Burstduration.keys()) >= 1:

            fig = plt.figure(dpi=300)

            plt.bar(*zip(*sorted(Burstduration.items())), color='m')
            plt.title(MEA)
            plt.ylabel('Burst count')
            plt.ylim(0, 400)
            plt.xlabel("Electrode")
            plt.savefig(figpath + str(MEA) + "_burst_duration_100ms.png", format='png')
            plt.close(fig)

        Burstduration500 = self.burstdranias_500ms(MEA)
        dict_to_file(dict=Burstduration500, filename=str(MEA) + "burstdranias_500ms", output_path=figpath)


        if len(Burstduration500.keys()) >= 1:

            fig2 = plt.figure(dpi=300)

            plt.bar(*zip(*sorted(Burstduration500.items())), color='m')
            plt.title(MEA)
            plt.ylabel('Burst count')
            plt.ylim(0, 400)
            plt.xlabel("Electrode")
            plt.savefig(figpath + str(MEA) + "_burst_duration_500ms.png", format='png')
            plt.close(fig2)

    def hist_ISI_MEA(self, figpath, MEA):

        """ Plots a histogram of the interspike interval of a SPKS_NeuronalData object and shows a default plot with a
         kernel density estimate and histogram with bin size determined automatically.

              Arguments:

                  SPKS_NeuronalData object
                  MEA(str): MEA number for plot title

              Returns:

                 Histogram plot.
              """

        # Method perfoms the analysis for the whole MEA or per electrode #

        # This can be changed inside the distplot and ax.set functions #

        grid_plot = plt.figure(dpi=300)
        plotnumber = 1

        intervals = dict()
        overallISI = list()

        initial_position = 0
        final_position = 1

        print('Performing the ISI histogram analysis')

        for electrode in self.spiketimes.keys():

            if electrode == 'duration':  # First position on the spiketimes dictionary is the duration of recording #

                continue

            if electrode == 'mock_spiketimes':  # First position on the spiketimes dictionary is the duration of recording #

                continue

            intervals[electrode] = list()  # Each list stores the ISIs of a given electrode

            while final_position < len(self.spiketimes[electrode]):  # Keeps the code into the arrays limit #

                ISI = self.spiketimes[electrode][final_position] - self.spiketimes[electrode][initial_position]

                intervals[electrode].append(ISI)
                overallISI.append(ISI)

                final_position = final_position + 1
                initial_position = initial_position + 1

            initial_position = 0
            final_position = 1

            if len(intervals[electrode]) == 0:

                continue

            grid_plot.add_subplot(7, 7, plotnumber)

            sns.set_context("paper")
            ax = sns.distplot(intervals[electrode], color='k', norm_hist=False, kde=False)
            ax.set(title=electrode)
                   #xscale="log", xlim=[10**3, 10**5], yscale="log", ylim=[10**-6, 10**-3])

            plotnumber = plotnumber + 1

        grid_plot.suptitle("MEA "+MEA, fontsize=10)
        plt.subplots_adjust(hspace=1, wspace=0.65)
        plt.savefig(figpath + str(MEA) + "_hist_ISI.png", format='png')
        plt.close(grid_plot)

        electrodenumber = self.active_electrodes()

        overallISI = np.array(overallISI)
        averageISI = overallISI.mean()

        return averageISI

    def IBI_visualisation(self, MEA):

        IBI = self.burstdranias_100ms(MEA)

        for electrode in IBI:

            if len(IBI[electrode]) == 0:

                continue

            plt.plot(IBI[electrode], label="Electrode_" + str(electrode))
            plt.title(MEA)
            plt.legend(fontsize=4)
            plt.ylabel('IBI(ms)')
            plt.ylim(0, 50)
            plt.xlabel("Inverval number")

    def visualise_rasters(self, figpath, MEA):

        """ Plots a raster for the spiketimes of each electrode of a SPKS_NeuronalData object

                    Arguments:

                        SPKS_NeuronalData object
                        MEA(str): MEA number for plot title
                        figpath(str): Full path of the location to save the output figure

                    Returns:

                       Raster plot per MEA
                    """

        fig = plt.figure(dpi=500)
        ax1 = fig.add_subplot(111)

        list_of_lists = list()

        for channel in self.spiketimes.keys():

            if channel == 'duration':

                continue

            list_of_lists.append(self.spiketimes[channel])

            #plt.plot(self.spiketimes[channel], np.repeat(int(channel), len(self.spiketimes[channel])), marker=2,
            #         label=channel)

        array_of_lists=np.array(list_of_lists)
        ax1.eventplot(positions=array_of_lists, linelengths=0.5)
        plt.title(MEA)
        #plt.legend(fontsize=4, loc='upper left')
        plt.ticklabel_format(axis="x", style="sci", scilimits=(0,0))
        plt.ylabel('Electrode recorded')
        plt.xlim(0, 250000)
        plt.xlabel("Spike time (ms)")

        savepath = figpath +  str(MEA) + "\\"

        plt.savefig(savepath+ str(MEA) + "_spiketimes_raster.png", format='png')
        #plt.close(fig)
# ----------------------------------------------------------------------------------------------------------------- #

# Functions for data visualisation #

# ----------------------------------------------------------------------------------------------------------------- #


def FR_perelectrode_barplot(figpath, firingrates, MEA):

    """ Computes the firing rates in Hz for all electrodes of a SPKS_NeuronalData object

        Arguments:

            figpath(str): Path to save the plot.
            firingrates(dict): Dictionary with electrode as keys and firing rates in Hz as values
            MEA(str): Multielectrode array number

        Returns:

           Bar plot with Firing Rates

        """

    if len(firingrates.keys()) > 1:

        fig = plt.figure(dpi=500)

        plt.bar(*zip(*sorted(firingrates.items())), color='k')
        plt.xlabel('Electrode')
        plt.title('MEA ' + MEA + ' firing rates')
        plt.ylim(0, 5)

        plt.savefig(figpath + str(MEA) + "_FR_Hz.png", format='png')
        plt.close(fig)


def generateMEA():

    """
    Adds the 8x8 MEA nodes to a graph G
    """

    G = nx.Graph()  # This generates your network using NetworkX

    for node_ID in range(1, 61):

        if node_ID < 7:
            y = 8 - node_ID
            G.add_node(node_ID + 11, pos=(1, y))
        else:
            pass
        if 6 < node_ID < 15:
            y = 15 - node_ID
            G.add_node(node_ID + 14, pos=(2, y))
        else:
            pass

        if 14 < node_ID < 23:
            y = 23 - node_ID
            G.add_node(node_ID + 16, pos=(3, y))
        else:
            pass

        if 22 < node_ID < 31:
            y = 31 - node_ID
            G.add_node(node_ID + 18, pos=(4, y))
        else:
            pass

        if 30 < node_ID < 39:
            y = 39 - node_ID
            G.add_node(node_ID + 20, pos=(5, y))
        else:
            pass

        if 38 < node_ID < 47:
            y = 47 - node_ID
            G.add_node(node_ID + 22, pos=(6, y))
        else:
            pass

        if 46 < node_ID < 55:
            y = 55 - node_ID
            G.add_node(node_ID + 24, pos=(7, y))
        else:
            pass

        if 54 < node_ID < 61:
            y = 62 - node_ID
            G.add_node(node_ID + 27, pos=(8, y))
        else:
            pass

    return G


def draw_and_save_graph(G, output_path, filename):

    fig = plt.figure(dpi=500)

    positions = nx.get_node_attributes(G, 'pos')  # Gets the positions of each node for the final plot
    nx.draw_networkx(G, positions, node_size=500, node_color='white', edgelist=G.edges())  # Drawing function
    nx.write_gml(G, output_path + filename + ".gml")  # Exporting graph for further analysis

    plt.savefig(output_path + filename + ".png", format='png')
    plt.close(fig)

# ----------------------------------------------------------------------------------------------------------------- #

# Functions for data writing #

# ----------------------------------------------------------------------------------------------------------------- #


def write_FRs(MEA, FR, filename, output_path):

    fullname = output_path + filename + ".txt"
    file = open(fullname, "w+")
    string_to_write = "Culture " + str(MEA) + " had a firing rate of " + str(FR) + " Hz."
    file.write(string_to_write)
    file.close()


def dict_to_file(dict, filename, output_path):

    """ Writes any dictionary to a text file

               Arguments:

                dict(dict): Dictionary to be written
                filename(str): name of the output file
                output_path(str): Full path of the output file

              Returns:

                 Output file

              """

    fullname = output_path + filename + ".txt"
    file = open(fullname, "w+")

    for keys in dict.keys():

        file.write(str(keys) + " " + str(dict[keys])+"\n")

    file.close()
