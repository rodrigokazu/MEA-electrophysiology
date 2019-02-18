import scipy.io
import numpy as np


class SPKS_NeuronalData:

    spiketimes = {}
    spikeshapes = {}

    def __init__(self, shapedata,time_array, occurrence_ms, channelids):

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
            self.spiketimes[key] = list()

            spike_number = len(input_occurrencedata['spiketimes'][0:60][channel][0])

            if spike_number > 4:  # Channels with less than 4 spikes are excluded from further analysis #

                self.spikeshapes[key] = list()
                transpose = np.transpose(input_shapedata['spikedata_cell'][0:60][channel][0])
                self.spikeshapes[key] = transpose

            else:

                del self.spiketimes[key]

                # Fills the arrays with the times of spikes in ms #

            if spike_number > 4:

                for spike_event in range(0, spike_number):

                    self.spiketimes[key].append(input_occurrencedata['spiketimes'][0:60][channel][0][spike_event][0])

        self.exclusion()  # Exclude channels after visual inspection #

    def exclusion(self):

        print("Please enter one channel to be excluded")
        channel = int(input())

        while channel != 0:

            del self.spiketimes[channel]
            del self.spikeshapes[channel]
            channel = input()
