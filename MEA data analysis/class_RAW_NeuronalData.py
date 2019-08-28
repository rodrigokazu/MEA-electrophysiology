import gc
import h5py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

    def recursive_spike_detection(self, MEA, folder):

        spiketimes = {}  # Dictionary that will contain the detected spiketimes
        valid_channels = list()  # List of valid channels, with 4 or more spikes and visually inspected
        threshold_array = {}  # Dictionary that will contain the threshold computations
        recur_spiketimes = {}
        recur_spikevoltages = {}
        detection_number = {}

        instant_spike_cutout = np.zeros(75)

        xaxis = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]

        flagmatrix = sp.csr_matrix((90, 6000000), dtype='float64')  # Positions to be ignored #

        # ------------------------------------------------------------------------------------------------------------ #

        for key in self.mcd_data:  # Creates the threshold lists

            if key != 'ms':

                threshold_array[key] = list()
                recur_spiketimes[key] = list()

        for key in self.mcd_data:

            fig = plt.figure()

            if key != 'ms':

                size = len(self.mcd_data[key])
                threshold = -5.5 * np.std(self.mcd_data[key])  # Sets the threshold in 5.5 STD
                threshold_array[key].append(threshold)
                spikes = 0

                while spikes < size:  # Flags detects spikes

                    cutout = 0

                    if self.mcd_data[key][spikes] < threshold:

                        fig = plt.figure()

                        while self.mcd_data[key][spikes+cutout] >= self.mcd_data[key][spikes+cutout+1] and cutout < 75:

                            cutout = cutout + 1

                        spike_apex = spikes + cutout  # Lowest point of the spike (i.e. spike time)
                        recur_spiketimes[key].append(self.mcd_data['ms'][spike_apex])
                        print("New spike at ", self.mcd_data['ms'][spike_apex])

                        for backwards in range(0, 25):  # Flags the descent of the spike

                            flagmatrix[int(key), int(spike_apex - backwards)] = True

                        for forwards in range(0, 50):  # Flags the raise of the spike

                            flagmatrix[int(key), spike_apex + forwards] = True

                        spikes = spike_apex + 50

                    else:

                        spikes = spikes + 1


        # File handling #

        file = folder + MEA + "_Analysis_Output.txt"
        f = open(file, 'w')
        f.write(str(recur_spiketimes))
        f.close()

        # Memory cleaning #

        del self
        gc.collect()
        print(time.asctime(time.localtime(time.time())))  # Prints the current time for profiling
