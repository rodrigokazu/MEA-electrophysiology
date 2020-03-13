from copy import deepcopy
from class_SPKS_NeuronalData import *
import gc
import h5py
import matplotlib.pyplot as plt
import numpy as np
import pickle
import seaborn as sns
from scipy import signal, io
import time

plt.switch_backend('agg')
plt.rcParams.update({'font.size': 5})


class RAW_NeuronalData:

    def __init__(self, uv_data, time_array, channelids):

        """ Reads multiple *.mat files with empirically recorded neuronal data from multielectrode arrays exported with the
         MCD_files_export_uV_and_mS_plus_METADATA.m script and generates a RAW_NeuronalData object

                Arguments:

                    uvdata (str): path to the *.hdf5 file containing voltage times
                    time_array (str): path to the *.mat file containing the recorded timestamps in ms
                    channelids (str): path to the *.mat file containing the recorded electrode numbers

                Returns:

                   RAW_NeuronalData object
                """

        self.mcd_data = {}

        file = h5py.File(uv_data, 'r')  # Generating a h5py File Object #
        array_of_arrays = np.array(file['voltagedata_cell'])  # Converts the object into a numpy array of arrays #

        recorded_uvdata = np.transpose(array_of_arrays)  # Transposes it since the data comes rotated #
        recorded_timedata = io.loadmat(time_array)
        recorded_channelids = io.loadmat(channelids)

        # The first index after it stands for the matrix line, the second one for the column #
        # Column ZERO has all the channel names, already in the correct order #

        self.mcd_data['ms'] = list()  # First entry of the dictionary will be the time in ms #
        self.mcd_data['ms'].extend(recorded_timedata['timedata'][0])

        # Then we add the channel IDs and the voltage data #

        for channel in range(0, 60):

            key = recorded_channelids['channelID_matrix'][channel][0][0]  # First column has the channel IDs #

            self.mcd_data[key] = list()
            self.mcd_data[key].extend(recorded_uvdata[channel])  # Filling the arrays with the voltages #

    def bandstop(self):

        """ Pass the all electrodes of a MEA recording stored as a RAW_NeuronalData object trough a bandstop filter of
        order 3 with cutoff frequencies of 60Hz and 40Hz.


            Returns:

               Filtered RAW_NeuronalData object
            """

        for key in self.mcd_data:

            if key != 'ms':

                self.mcd_data[key] = butter_bandstop_filter(data=self.mcd_data[key], lowcut=40, highcut=60, fs=25000,
                                                            order=3)

        return self

    def dynamic_thresholding(self, key, spiketimes, spikeshapes, spikeapexes, threshold_array):

        """ Reads a RAW_NeuronalData object channel(electrode) and extract spikes for it utilising the recursive spike
        detection algorithm devised at the University of Reading, altering the dictionaries and returning if a next round
        is needed

            Arguments:

                key(str): Electrode number
                spiketimes(dict): Dictionary to save the spiketimes
                spikeshapes(dict): Dictionary to save the spikeshapes
                spikeapexes(dict): Dictionary to save the spikeapexes (peaks)
                threshold_array(dict): Dictionary of the thresholds utilised

            Returns:

               Detection signpost
            """

        detection = 0
        detection_time = 0

        size = len(self.mcd_data[key])
        threshold = -5.5 * np.std(self.mcd_data[key])  # Sets the threshold in 5.5 STD #
        threshold_array[key].append(threshold)

        spikes = 0
        occurence = 0

        while spikes < size:  # Flags detected spikes #

            cutout = 0

            if self.mcd_data[key][spikes] < threshold:

                detection = 1

                while self.mcd_data[key][spikes + cutout] >= self.mcd_data[key][spikes + cutout + 1] and cutout < 75:

                    cutout = cutout + 1

                spike_apex = spikes + cutout  # Lowest point of the spike (i.e. spike time) #

                spikeapexes[key].append(self.mcd_data[key][spike_apex])
                spikeshapes[key][occurence] = np.zeros(75)

                for backwards in range(0, 25):  # Flags the descent of the spike

                    spikeshapes[key][occurence][24 - backwards] = self.mcd_data[key][int(spike_apex - backwards)]

                for forwards in range(0, 50):  # Flags the raise of the spike

                    spikeshapes[key][occurence][24 + forwards] = self.mcd_data[key][spike_apex + forwards]

                spikes = spike_apex - 25  # Sets the investigated point to the beginning of the spike before removal

                occurence = occurence + 1

                for del_backwards in range(0, 25):  # Clears for dynamic thresholding

                    self.mcd_data[key] = np.delete(self.mcd_data[key], spike_apex - del_backwards)

                for del_forwards in range(0, 50):  # Clears for dynamic thresholding

                    self.mcd_data[key] = np.delete(self.mcd_data[key], spike_apex + del_forwards)

                if occurence != 1:  # Accounting for the excluded spikes

                    conversion_factor = occurence - 1
                    conversion_factor = 75 * conversion_factor
                    detection_time = spikes + conversion_factor
                    spiketimes[key].append(self.mcd_data['ms'][detection_time])

                size = len(self.mcd_data[key])  # Updates the size
                spikes = spikes + 1  # Moves the analysed point

            else:

                spikes = spikes + 1

        return detection

    def electrode_spike_detection(self, key, spiketimes, spikeshapes, spikeapexes, threshold_array):

        """ Reads a RAW_NeuronalData object channel(electrode) and extract spikes for it utilising the recursive spike
       detection algorithm devised at the University of Reading dynamic_thresholding(self, key, spiketimes, spikeshapes,
       spikeapexes, threshold_array), altering the dictionaries.

           Arguments:

               key(str): Electrode number
               spiketimes(dict): Dictionary to save the spiketimes
               spikeshapes(dict): Dictionary to save the spikeshapes
               spikeapexes(dict): Dictionary to save the spikeapexes (peaks)
               threshold_array(dict): Dictionary of the thresholds utilised

           """

        if key != 'ms':

            detection = 1
            round = 1

            while detection == 1:

                print("Round number ", round, " for electrode ", key)

                detection = self.dynamic_thresholding(key, spiketimes, spikeshapes, spikeapexes, threshold_array)
                round = round + 1

        print("Finished for electrode ", key)

    def exclusion(self):

        """ Remove electrodes from the RAW_NeuronalData object

            Arguments:

                RAW_NeuronalData object

            Returns:

               Updated RAW_NeuronalData object
            """

        print("Please enter one channel to be excluded")
        channel = int(input())

        while channel != 0:

            del self.mcd_data[channel]
            channel = input()

        return self

    def highpass(self):

        """ Creates a Butterworth filter with a cutoff of 0.02 times the Nyquist rate, or 20 Hz and runs it through a
        RAW_NeuronalData object with sampling rate of 25000000 milisamples per second, 25000 Hz.

                Arguments:

                    RAW_NeuronalData object

                Returns:

                   Filtered RAW_NeuronalData object
                """

        b, a = signal.butter(2, 0.02, btype='highpass')

        for key in self.mcd_data:

            if key != 'ms':

                self.mcd_data[key] = signal.filtfilt(b, a, self.mcd_data[key])

        return self

    def parallel_recursive_spike_detection(self):

        """ Attempt to paralelise the detection. Reads a RAW_NeuronalData object and extract spikes for each channel
        utilising the recursive spike detection algorithm devised at the University of Reading, converting it to a
        SPKS_NeuronalData object

            Arguments:

                RAW_NeuronalData object

            Returns:

               SPKS_NeuronalData object
            """

        print('Now copying the time series.')

        spiketimes = dict()  # Dictionary that will contain the detected spiketimes
        spikeshapes = dict()  # Dictionary that will contain the detected spikeshapes
        spikeapexes = dict()  # Dictionary that will contain the detected spikeapexes
        threshold_array = dict()  # Dictionary that will contain the threshold computations

        # ------------------------------------------------------------------------------------------------------------ #

        for key in self.mcd_data:  # Creates the relevant lists #

            if key != 'ms':
                threshold_array[key] = list()
                spiketimes[key] = list()
                spikeshapes[key] = dict()
                spikeapexes[key] = list()

        pool = mp.Pool(mp.cpu_count())

        for key in self.mcd_data:  # Runs the actual detection per electrode #

            pool.apply(self.electrode_spike_detection,
                       args=(self, key, spiketimes, spikeshapes, spikeapexes, threshold_array))

        del self
        gc.collect()

    def recursive_spike_detection(self, MEA, figpath):

        """ Reads a RAW_NeuronalData object and extract spikes for each channel utilising the recursive spike detection
        algorithm devised at the University of Reading, converting it to a SPKS_NeuronalData object

            Arguments:

                RAW_NeuronalData object

            Returns:

               SPKS_NeuronalData object
            """

        start = time.asctime(time.localtime(time.time()))  # Profiling

        spiketimes = dict()  # Dictionary that will contain the detected spiketimes
        spikeshapes = dict()  # Dictionary that will contain the detected spikeshapes
        spikeapexes = dict()  # Dictionary that will contain the detected spikeapexes
        threshold_array = dict()  # Dictionary that will contain the threshold computations

        # ------------------------------------------------------------------------------------------------------------ #

        for key in self.mcd_data:  # Creates the relevant lists #

            if key != 'ms':

                threshold_array[key] = list()
                spiketimes[key] = list()
                spikeshapes[key] = dict()
                spikeapexes[key] = list()

        for key in self.mcd_data:  # Runs the actual detection per electrode #

            self.electrode_spike_detection(key, spiketimes, spikeshapes, spikeapexes, threshold_array)

        finish = time.asctime(time.localtime(time.time()))

        plot_thresholds(figpath=figpath, MEA=MEA, threshold_array=threshold_array)

        print("Started the recursive detection at", start, "and finished at", finish)  # Profiling

        duration = len(self.mcd_data['ms'])

        spike_data = SPKS_NeuronalData(input="RAWdata", occurrence_ms=spiketimes, shapedata=spikeshapes,
                                       duration=duration)

        file_pi = open(figpath + MEA + '.obj', 'wb')
        pickle.dump(spike_data, file_pi)

        del self
        gc.collect()

        return spike_data

# ----------------------------------------------------------------------------------------------------------------- #

# Filtering functions #

# ----------------------------------------------------------------------------------------------------------------- #


def butter_bandstop(lowcut, highcut, fs, order):

    """Generate the coefficients for a bandpass filter, give butter() the filter order, the cutoff frequencies
    Wn=[low, high] (expressed as the fraction of the Nyquist frequency, which is half the sampling frequency) and the
    band type btype="band".

                Arguments:

                    lowcut(int): Lower cut frequency
                    highcut(int): Higher cut frequency
                    fs(int): Frequency of sampling
                    order(int): Filter order

                Returns:

                   Filter coefficients b and a

                """

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = signal.butter(order, [low, high], btype='bandstop')

    return b, a


def butter_bandstop_filter(data, lowcut, highcut, fs, order):

    """ Pass a electrode voltage train through a bandpass filter


        Arguments:

            data(list): Data to be filtered
            lowcut(int): Lower cut frequency
            highcut(int): Higher cut frequency
            fs(int): Frequency of sampling
            order(int): Filter order

        Returns:

           Filtered data
        """

    b, a = butter_bandstop(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)

    return y


# ----------------------------------------------------------------------------------------------------------------- #

# Mock data #

# ----------------------------------------------------------------------------------------------------------------- #

def noise():

    # Generates channel noise using a Ornstein-Uhlenbeck process #

    duration = np.linspace(0, 300, 25000)
    N = len(duration)
    noise = np.zeros(N)
    h = duration[1] - duration[0]
    tau = 0.5
    Xrest = 0
    Xthres = -15
    noise[0] = Xrest

    I = lambda t: 0.0

    for i in range(N-1):

        noise[i + 1] = noise[i] - h*(noise[i] - Xrest)/tau + np.sqrt(h)*np.random.normal(scale=10.0) + I(duration)

    return duration, noise


def poisson_spike_generator():

    spikes = []
    num_cells = 1

    # Generates spike data using a simple Poisson-like generator #

    for i in range(num_cells):

        isi = np.random.poisson(size=300)
        spikes.append(np.cumsum(isi))

    return spikes

# ----------------------------------------------------------------------------------------------------------------- #

# Functions for data writing #

# ----------------------------------------------------------------------------------------------------------------- #


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
    file.write(str(dict))
    file.close()

# ----------------------------------------------------------------------------------------------------------------- #

# Functions for data visualisation #

# ----------------------------------------------------------------------------------------------------------------- #


def plot_thresholds(figpath, MEA, threshold_array):

    """ Plots the evolution of the threshold detection

            Arguments:

                threshold_array(dict): Dictionary with the detected thresholds from the recursive detection.
                MEA(str): Data file being analysed
                figpath(str): Where to plot the data (full path)

          Returns:

              Saved plot.

           """

    for electrode in threshold_array.keys():

        fig = plt.figure(dpi=300)

        ax = sns.scatterplot(data=np.array(threshold_array[str(electrode)]))
        ax.set(title="MEA " + str(MEA) + "Electrode " + str(electrode))
        plt.ylabel("Voltage (uV)")
        plt.xlabel("Instant threshold")

        plt.savefig(figpath + "MEA_" + str(MEA) + "_Electrode_" + str(electrode) + "_thresholds_.png", format='png')
        plt.close(fig)


def plot_rawdata_singlechannel(channeldata, channelnumber, recursiveround, figpath):

    """ Reads a RAW_NeuronalData object channel(electrode) and plots the raw voltage data

          Arguments:

              channeldata(list): Raw voltage data for a given electrode.
              channelnumber(str): Electrode name or number
              recursiveround(str): Round of analysis (if using the recursive spike detection)
              figpath(str): Where to plot the data (full path)

        Returns:

            Saved plot.

          """

    fig = plt.figure(dpi=300)

    plt.plot(channeldata)

    plt.ylim(bottom=-80, top=30)
    plt.ylabel("Voltage (uV)")
    plt.xlim(left=0, right=6000000)
    plt.xlabel("Raw data points")

    plt.savefig(figpath + str(channelnumber) + "O3_r_" + str(recursiveround) + ".png", format='png')
    plt.close(fig)


def plot_spike(voltage, occurrence, figpath):

    """ Plots a detected spike

          Arguments:

              voltage(list): Raw voltage data for a given electrode.
              occurrence(str): Spike number
              figpath(str): Where to plot the data (full path)

        Returns:

            Saved plot.

          """

    fig = plt.figure(dpi=300)

    plt.plot(voltage)

    plt.ylim(bottom=-80, top=30)
    plt.ylabel("Voltage (uV)")
    plt.xlim(left=0, right=75)
    plt.xlabel("Data points")

    plt.savefig(figpath + str(occurrence) + "_spike_.png", format='png')
    plt.close(fig)


def visualise_spikes_generated(output_path):

    spikes = poisson_spike_generator()

    # Visualise #

    fig = plt.figure(dpi=500)

    filename = 'spikes'
    cells = [1]

    for cell in range(len(spikes)):

        plt.plot(spikes[cell], np.repeat(cells[cell], len(spikes[cell])), marker='o')

    plt.ylabel("Electrode number")
    plt.xlabel("Spike times")
    plt.title("Poisson Spiking")

    plt.savefig(output_path + filename + ".png", format='png')
    plt.close(fig)


def visualise_noise(output_path, noise):

    filename = "MEA_modelled_noise"

    sns.set_palette(sns.dark_palette("purple"))

    ax = sns.lineplot(x=noise[0], y=noise[1])

    plt.savefig(output_path + filename + ".png", format='png')