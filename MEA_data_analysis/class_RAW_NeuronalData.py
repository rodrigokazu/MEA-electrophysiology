from copy import deepcopy
import gc
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy import io, signal, sparse as sp
import time


class RAW_NeuronalData:

    def __init__(self, uv_data, time_array, channelids):

        self.mcd_data = {}

        file = h5py.File(uv_data, 'r')  # Generating a h5py File Object #
        array_of_arrays = np.array(file['voltagedata_cell'])  # Converts the object into a numpy array of arrays #

        recorded_uvdata = np.transpose(array_of_arrays)  # Transposes it since the data comes rotated #
        recorded_timedata = io.loadmat(time_array)
        recorded_channelids = io.loadmat(channelids)

        # The first index after it stands for the matrix line, the second one for the column #
        # Column ZERO has all the channel names, already in the correct order #

        self.mcd_data['ms'] = list()  # First entry of the dictionary will be the time in ms #

        record_duration = len(recorded_timedata['timedata'][0])

        for duration in range(0, record_duration-200):

            self.mcd_data['ms'].append(recorded_timedata['timedata'][0][duration])

        # Then we add the channel IDs and the voltage data #

        for channel in range(0, 60):

            size = len(recorded_uvdata[channel])-2
            key = recorded_channelids['channelID_matrix'][channel][0][0]  # First column has the channel IDs #
            self.mcd_data[key] = list()

            for voltage in range(0, size):

                self.mcd_data[key].append(recorded_uvdata[channel][voltage])  # Filling the arrays with the voltages #

    def exclusion(self):

        print("Please enter one channel to be excluded")
        channel = int(input())

        while channel != 0:

            del self.mcd_data[channel]
            channel = input()

        return self

    # ------------------------------------------------------------------------------------------------------------- #

    # My sampling rate is 25000000 milisamples per second, 25000 Hz #

    # Now create a Butterworth filter with a cutoff of 0.02 times the Nyquist rate, or 20 Hz #

    # ------------------------------------------------------------------------------------------------------------- #

    def highpass(self):

        b, a = signal.butter(2, 0.02)

        for key in self.mcd_data:

            if key != 'ms':

                self.mcd_data[key] = signal.filtfilt(b, a, self.mcd_data[key])

        return self

    def recursive_spike_detection(self):

        original_raw_timeseries = deepcopy(self)
        print('Now copying the time series.')

        spiketimes = dict()  # Dictionary that will contain the detected spiketimes
        spikeshapes = dict()  # Dictionary that will contain the detected spikeshapes
        spikeapexes = dict()  # Dictionary that will contain the detected spikeapexes
        valid_channels = list()  # List of valid channels, with 4 or more spikes and visually inspected #
        threshold_array = dict()  # Dictionary that will contain the threshold computations

        detection_number = dict()

        # ------------------------------------------------------------------------------------------------------------ #

        for key in self.mcd_data:  # Creates the relevant lists #

            if key != 'ms':

                threshold_array[key] = list()
                spiketimes[key] = list()
                spikeshapes[key] = dict()
                spikeapexes[key] = list()

        for key in self.mcd_data:  # Runs the actual detection per electrode #

            if key != 'ms':

                detection = 1
                round = 1

                while detection == 1:

                    figpath = "C:\\Users\\rodri\\Dropbox\\PhD\\Thesis\\Analysis Pipeline\\BEL_Datafiles_and_Scripts" \
                            "\\BEL_Python_Files\\Debug graphs\\Dynamic threshold localtest\\MEA_10672_DIV21_Channel_"

                    plot_rawdata_singlechannel(self.mcd_data[key], key, round, figpath)
                    detection = self.dynamic_thresholding(key, spiketimes, spikeshapes, spikeapexes, threshold_array)
                    round = round + 1

        del self
        gc.collect()
        print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling

    def dynamic_thresholding(self, key, spiketimes, spikeshapes, spikeapexes, threshold_array):

        detection = 0

        size = len(self.mcd_data[key])
        threshold = -5.5 * np.std(self.mcd_data[key])  # Sets the threshold in 5.5 STD #
        threshold_array[key].append(threshold)

        spikes = 0
        occurence = 0

        while spikes < size:  # Flags detected spikes #

            cutout = 0

            if self.mcd_data[key][spikes] < threshold:

                detection = 1

                while self.mcd_data[key][spikes+cutout] >= self.mcd_data[key][spikes+cutout+1] and cutout < 75:

                    cutout = cutout + 1

                spike_apex = spikes + cutout  # Lowest point of the spike (i.e. spike time) #

                spiketimes[key].append(self.mcd_data['ms'][spike_apex])
                spikeapexes[key].append(self.mcd_data[key][spike_apex])
                spikeshapes[key][occurence] = np.zeros(75)

                for backwards in range(0, 25):  # Flags the descent of the spike

                    spikeshapes[key][occurence][24 - backwards] = self.mcd_data[key][int(spike_apex - backwards)]

                for forwards in range(0, 50):  # Flags the raise of the spike

                    spikeshapes[key][occurence][24 + forwards] = self.mcd_data[key][spike_apex + forwards]

                spikes = spike_apex - 25  # Sets the investigated point to the beginning of the spike before removal

                for del_backwards in range(0, 25):  # Clears for dynamic thresholding

                    self.mcd_data[key] = np.delete(self.mcd_data[key], spike_apex - del_backwards)

                for del_forwards in range(0, 50):   # Clears for dynamic thresholding

                    self.mcd_data[key] = np.delete(self.mcd_data[key], spike_apex + del_forwards)

                size = len(self.mcd_data[key])
                spikes = spikes + 1

            else:

                spikes = spikes + 1

        return detection


def plot_rawdata_singlechannel(channeldata, channelnumber, recursiveround, figpath):

    fig = plt.figure(dpi=500)

    plt.plot(channeldata)

    plt.ylim(bottom=-60, top=10)
    plt.ylabel("Voltage")
    plt.xlim(left=0, right=6000000)
    plt.xlim("Raw data points")

    plt.savefig(figpath + str(channelnumber) + "_round_" + str(recursiveround) + "_.png", format='png')
    plt.close(fig)

    print("Electrode ", channelnumber, "round of detection number ", recursiveround)