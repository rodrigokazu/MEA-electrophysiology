import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)  # Ignores pointless matplotlib warnings
plt.rcParams.update({'font.size': 8})


class SPKS_NeuronalData:

    def __init__(self, shapedata, time_array, occurrence_ms, channelids):

        self.spiketimes = {}
        self.spikeshapes = {}

        # Imports data #

        recorded_timedata = scipy.io.loadmat(time_array)
        recorded_channelids = scipy.io.loadmat(channelids)
        input_occurrencedata = scipy.io.loadmat(occurrence_ms)
        input_shapedata = scipy.io.loadmat(shapedata)

        # The first index after it stands for the matrix line, the second one for the column #
        # Column ZERO has all the channel names, already in the correct order #

        record_duration = len(recorded_timedata['timedata'][0])

        self.spiketimes['duration'] = record_duration  # First entry of the dictionary will be the time in ms #

        for channel in range(0, 60):

            key = recorded_channelids['channelID_matrix'][channel][0][0]  # First column has the channel IDs #

            spike_number = len(input_occurrencedata['spiketimes'][0:60][channel][0])

            if spike_number > 4:  # Channels with less than 4 spikes are excluded from further analysis #

                # Stores the Spike Shapes #

                self.spikeshapes[key] = list()
                transpose = np.transpose(input_shapedata['spikedata_cell'][0:60][channel][0])
                self.spikeshapes[key] = transpose

                # Fills the arrays with the times of spikes in ms #

                self.spiketimes[key] = list()

                for spike_event in range(0, spike_number):

                    self.spiketimes[key].append(input_occurrencedata['spiketimes'][0:60][channel][0][spike_event][0])

        self.exclusion()  # Exclude channels after visual inspection #

    def exclusion(self):

        print("Please enter one channel to be excluded (enter zero to skip to the next MEA recording) from: \n ", self.spiketimes.keys())

        channel = input()

        while channel != '0':

            del self.spiketimes[str(channel)]
            del self.spikeshapes[str(channel)]
            channel = input()

# ----------------------------------------------------------------------------------------------------------------- #

# Methods for electrophysiological calculations #

# ----------------------------------------------------------------------------------------------------------------- #

    def electrode_FR(self, MEA):

        firingrates = {}

        # Compute the record duration to seconds from ms #

        duration_ms = self.spiketimes['duration']
        duration_s = duration_ms / 1000

        for key in self.spikeshapes:

            # Compute the total spike number per electrode #

            spike_number = len(self.spikeshapes[key])

            # Compute and store the firing rates #

            electrode_fr_s = spike_number / duration_s
            firingrates[key] = electrode_fr_s

#        if len(self.spiketimes.keys()) > 1:

#           plt.bar(*zip(*sorted(firingrates.items())), color='y')
#            plt.xlabel('Electrode')
#            plt.title('MEA ' + MEA + ' firing rates')
#            plt.ylim(0, 0.1)

#        print(firingrates)

        return firingrates

    def MEA_overall_firingrate(self, MEA):

        individual_fr = self.electrode_FR(MEA)
        spikecount = 0

        for key in individual_fr:

            spikecount = individual_fr[key] + spikecount

        if len(self.spiketimes.keys()) > 1:

            active = len(self.spiketimes.keys()) - 1

            overall_firingrate_s = spikecount / active

        else:

            overall_firingrate_s = 0

        return overall_firingrate_s

# ----------------------------------------------------------------------------------------------------------------- #

# Computes burst counts and profiles according to Dranias, 2015 #

# Bursts were defined as the presence of four spikes in a 100ms with an interval of 50ms to the next spike after #

# ----------------------------------------------------------------------------------------------------------------- #

    def burstdranias_100ms(self, MEA):

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

# ----------------------------------------------------------------------------------------------------------------- #

# Computes burst counts and profiles  #

# Bursts were defined as the presence of four spikes in a 500ms based on the timescales of my dataset #

# ----------------------------------------------------------------------------------------------------------------- #


    def burstdranias_500ms(self, MEA):

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

        #ax = sns.distplot(burstprofile[electrode], color='y')
        #ax.set(title='MEA ' + MEA)

        return burstduration


# ----------------------------------------------------------------------------------------------------------------- #

# Methods for data visualisation #

# ----------------------------------------------------------------------------------------------------------------- #

    # Show a default plot with a kernel density estimate and histogram with bin size determined automatically #

    def hist_ISI_MEA(self, MEA):

        # Method perfoms the analysis for the whole MEA or per electrode #

        # This can be changed inside the distplot and ax.set functions #

        grid_plot = plt.figure(dpi=100)
        plotnumber = 1

        intervals = dict()
        overallISI = list()

        initial_position = 0
        final_position = 1

        for electrode in self.spiketimes.keys():

            if electrode == 'duration':  # First position on the spiketimes dictionary is the duration of recording #

                continue

            print('Channel analysed: ', electrode, 'with', len(self.spiketimes[electrode]), 'spikes.')
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

            grid_plot.add_subplot(8, 8, plotnumber)

            ax = sns.distplot(intervals[electrode], color='y')
            ax.set(title=electrode, xscale="log", yscale="log") 

            plotnumber = plotnumber + 1

        grid_plot.suptitle("MEA "+MEA, fontsize=16)
        plt.subplots_adjust(hspace=1, wspace=0.65)
        plt.show()

    # Data visualisation for IBI per MEA #

    def IBI_visualisation(IBI):

        IBI = spike_data.burstdranias_100ms(MEA)

        for electrode in IBI:

            if len(IBI[electrode]) == 0:
                continue

            plt.plot(IBI[electrode], label="Electrode_" + str(electrode))
            plt.title(MEA)
            plt.legend(fontsize=4)
            plt.ylabel('IBI(ms)')
            plt.ylim(0, 50)
            plt.xlabel("Inverval number")

    # Data visualisation for burst duration per MEA #

    def Burstduration_visualisation(Burstduration):

        Burstduration = spike_data.burstdranias_100ms(MEA)

        for electrode in Burstduration:

            if len(Burstduration[electrode]) == 0:
                continue

            plt.bar(*zip(*sorted(Burstduration[electrode].items())), color='m')
            plt.title(MEA)
            plt.ylabel('Burst size')
            plt.ylim(0, 400)
            plt.xlabel("Electrode" + str(electrode))
