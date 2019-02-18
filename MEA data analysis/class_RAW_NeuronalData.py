from scipy import io, signal
import h5py
import numpy as np


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