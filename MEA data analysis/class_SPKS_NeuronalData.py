import scipy.io
import numpy as np
import matplotlib.pyplot as plt


class SPKS_NeuronalData:

    spiketimes = {}
    spikeshapes = {}

    def __init__(self, shapedata, time_array, occurrence_ms, channelids):

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

    # --------------------------------------------------------------------------------------------- #

    # Methods for electrophysiological calculations #

    # --------------------------------------------------------------------------------------------- #

    def electrode_FR(self):

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

        #            print('Electrode', key, 'has a firing rate of', electrode_fr_s)

        return firingrates

    def MEA_overall_firingrate(self):

        individual_fr = self.electrode_FR()
        spikecount = 0

        for key in individual_fr:
            spikecount = individual_fr[key] + spikecount

        overall_firingrate_s = spikecount / 60

        return overall_firingrate_s

    # Computes burst counts and profiles according to Dranias, 2015 #

    # Bursts were defined as the presence of four spikes in a 100ms with an interval of 50ms to the next spike after #

    def burstdranias(self):

        # Variables #

        burstcount = 0  # Overall burst count #
        burstprofile = dict()
        electrodecount = dict()

        spikecount = 0

        initial_pos = 0  # Position on spiketimes array #
        final_pos = 1

        for electrode in self.spiketimes.keys():  # Computing it for all channels #

            if electrode == 'duration':  # First position on the spiketimes dictionary is the duration of recording #

                continue

            print('Channel analysed: ', electrode)
            burstprofile[electrode] = dict()
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

                if self.spiketimes[electrode][final_pos + 1] - self.spiketimes[electrode][final_pos] <= 50:

                    burstcount = burstcount + 1
                    burstprofile[electrode][burstevent] = list()

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

        return burstcount, electrodecount, burstprofile

    # --------------------------------------------------------------------------------------------- #

    # Methods for data visualisation #

    # --------------------------------------------------------------------------------------------- #

    def hist_ISI(self, MEA):

        fig = plt.figure()

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

        fig.add_subplot()
        plt.hist(overallISI, bins=100, label=MEA)  # Plot per MEA
        plt.legend(loc=1, prop={'size': 8})  # Use for the electrode specific plot
        plt.ylabel('Frequency')
        plt.xticks(np.linspace(0, 7000))
        plt.xlabel('ISIs (ms)')
        plt.show()
