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
plt.rcParams.update({'font.size': 10})


class RAW_NeuronalData:

    def __init__(self, uv_data, input, time_array, channelids):

        """ Reads multiple *.mat files with empirically recorded neuronal data from multielectrode arrays exported with the
         MCD_files_export_uV_and_mS_plus_METADATA.m script and generates a RAW_NeuronalData object

                Arguments:

                    uvdata (str): path to the *.hdf5 file containing voltage times
                    input(str): input source
                    time_array (str): path to the *.mat file containing the recorded timestamps in ms
                    channelids (str): path to the *.mat file containing the recorded electrode numbers

                Returns:

                   RAW_NeuronalData object
                """

        if input == "MATLAB":

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

        elif input == "RAWdata":

            self.mcd_data = {}

            self.mcd_data['mock_spiketimes'] = list()
            self.mcd_data['mock_spiketimes'].extend(time_array['mock_spiketimes'])

            for channel in time_array.keys():

                self.mcd_data['ms'] = list()  # First entry of the dictionary will be the time in ms #
                self.mcd_data['ms'].extend(time_array[channel])

                if channel != 'mock_spiketimes':  # Avoiding the mock spiketimes

                    self.mcd_data[channel] = list()
                    self.mcd_data[channel].extend(uv_data[channel])  # Filling the arrays with the voltages #

    def bandstop(self):

        """ Pass the all electrodes of a MEA recording stored as a RAW_NeuronalData object through a bandstop filter of
        order 3 with cutoff frequencies of 60Hz and 40Hz.


            Returns:

               Filtered RAW_NeuronalData object
            """

        for key in self.mcd_data:

            if key != 'ms':

                if key != 'mock_spiketimes':

                    self.mcd_data[key] = butter_bandstop_filter(data=self.mcd_data[key], lowcut=40, highcut=60, fs=25000,
                                                            order=3)

        return self

    def dynamic_thresholding(self, key, spiketimes, spikeshapes, spikeapexes, threshold_array, round, figpath):

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

                    spikeshapes[key][occurence][24 - backwards] = self.mcd_data[key][spike_apex - backwards]

                for forwards in range(0, 50):  # Flags the raise of the spike

                    spikeshapes[key][occurence][24 + forwards] = self.mcd_data[key][spike_apex + forwards]

                plot_spike(voltage=spikeshapes[key][occurence], occurrence=str(occurence), electrode=key,
                           figpath=figpath, round=str(round))

                for del_backwards in range(0, 25):  # Clears for dynamic thresholding

                    self.mcd_data[key] = np.delete(self.mcd_data[key], spike_apex - del_backwards)

                spike_apex = spike_apex - 25

                for del_forwards in range(0, 50):  # Clears for dynamic thresholding

                    self.mcd_data[key] = np.delete(self.mcd_data[key], spike_apex)

                spike_apex = spikes + cutout

                occurence = occurence + 1

                if occurence != 0:  # Accounting for the excluded spikes

                    detection_time = spike_apex  # 25 samples per ms
                    spiketimes[key].append(self.mcd_data['ms'][detection_time])

                size = len(self.mcd_data[key])  # Updates the size
                spikes = spikes - 25  # Sets the investigated point to the beginning of the spike before removal
                # spikes = spikes + 63  # Refractory period of 2.5 ms

            else:

                spikes = spikes + 1

        return detection

    def electrode_spike_detection(self, key, spiketimes, spikeshapes, spikeapexes, threshold_array, figpath):

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

            if key != 'mock_spiketimes':

                detection = 1
                round = 0

                while detection == 1:

                    print("Round number ", round, " for electrode ", key)

                    # plot_rawdata_singlechannel(self.mcd_data[key], channelnumber=str(key), recursiveround=str(round), figpath=figpath)

                    detection = self.dynamic_thresholding(key=key, spiketimes=spiketimes, spikeshapes=spikeshapes,
                                                          spikeapexes=spikeapexes, threshold_array=threshold_array,
                                                          round=str(round), figpath=figpath)

                    round = round + 1

        # plot_rawdata_singlechannel(self.mcd_data[key], channelnumber=str(key), recursiveround=str(round), figpath=figpath)

        print("Finished for electrode ", key)

    def exclusion(self, channel):

        """ Remove electrodes from the RAW_NeuronalData object, can be used with user input

            Arguments:

                RAW_NeuronalData object

            Returns:

               Updated RAW_NeuronalData object
            """

        # print("Please enter one channel to be excluded")
        # channel = int(input())

        #while channel != 0:

        del self.mcd_data[channel]
            #channel = input()

        return self

    def bandstop_resonator(self):

        """ Creates a Notch filter with Q = 10, and fs = 50Hz and runs it through a RAW_NeuronalData object with
        sampling rate of 25000 samples per second, 25000 Hz.

                       Arguments:

                           RAW_NeuronalData object

                       Returns:

                          Filtered RAW_NeuronalData object
                       """

        b, a = notch_bandstopresonator(f0=0.004, Q=10)

        for key in self.mcd_data:

            if key != 'ms':

                if key != 'mock_spiketimes':

                    self.mcd_data[key] = signal.filtfilt(b, a, self.mcd_data[key])

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

                if key != 'mock_spiketimes':

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

                if key != 'mock_spiketimes':

                    threshold_array[key] = list()
                    spiketimes[key] = list()
                    spikeshapes[key] = dict()
                    spikeapexes[key] = list()

        for key in self.mcd_data:  # Runs the actual detection per electrode #

            if key != 'ms':

                if key != 'mock_spiketimes':

                    self.electrode_spike_detection(key=key, spiketimes=spiketimes, spikeshapes=spikeshapes,
                                                   spikeapexes=spikeapexes, threshold_array=threshold_array,
                                                   figpath=figpath)

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

    b, a = signal.butter(N=order, Wn=[low, high], btype='bandstop')

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

    b, a = butter_bandstop(lowcut=lowcut, highcut=highcut, fs=fs, order=order)
    y = signal.lfilter(b, a, data)

    return y


def notch_bandstopresonator(f0, Q):

    b, a = signal.iirnotch(w0=f0, Q=Q)

    return b, a

# ----------------------------------------------------------------------------------------------------------------- #

# Mock data #

# ----------------------------------------------------------------------------------------------------------------- #


def create_mockdata(output_path, electrode):

    """ Creates mock data for a given electrode using the spike generator and the template provided

             Arguments:

              output_path(str): Location to save the results
              electrode(str): Electrode number to generate the mock data for

            Returns:

               Mock data as a RAW_NeuronalData object
       """

    uv_data = {}
    time_array = {}
    channelids = {}

    channels = list()
    channels.append(str(electrode))

    fullname = output_path + "Mock_" + str(electrode) + ".txt"
    file = open(fullname, "w+")

    for electrode in channels:

        channelids[electrode] = list()

        channel_noise = noise()  # Creates noise for the channel

        Threshold_noise = "Noise threshold for" + str(electrode) + "=" + str(channel_noise[2])

        file.write(Threshold_noise)

        spikes = exponential_spike_generator()  # Randomly generated spike times

        time_array['mock_spiketimes'] = spikes

        Mock_electrode_spiketimes = "Spike times for" + str(electrode) + "=" + str(spikes[0][0])

        file.write(Mock_electrode_spiketimes)

        Mock_electrode_detections = "Spike number for" + str(electrode) + "=" + str(spikes[1])

        file.write(Mock_electrode_detections)

        file.close()

        template = [1.77083333333333, 1.04166666666667, 1.97916666666667, 2.81250000000000, 1.87500000000000, 1.56250000000000,
                    2.70833333333333, 2.81250000000000, 3.12500000000000, 3.33333333333333, 2.50000000000000, 1.14583333333333,
                    1.77083333333333, 2.50000000000000, 0.937500000000000, 0.729166666666667, 1.66666666666667, 2.500000000000,
                    1.35416666666667, 1.97916666666667, 5.93750000000000, 12.5000000000000, 18.5416666666667, 18.4375000000000,
                    4.16666666666667, -21.6666666666667, -39.7916666666667, -40, -31.4583333333333, -22.5000000000000,
                    -17.2916666666667, -14.5833333333333, -10.8333333333333, -8.22916666666667, -6.77083333333333, -3.12500000,
                    -2.18750000000000, -1.45833333333333, -0.937500000000000, 0.104166666666667, 3.02083333333333, 2.2916666667,
                    0.416666666666667, 0.625000000000000, 2.91666666666667, 3.22916666666667, 3.75000000000000, 6.1458333333333,
                    6.56250000000000, 6.97916666666667, 6.04166666666667, 5.41666666666667, 5.10416666666667, 5.10416666666667,
                    6.66666666666667, 5.52083333333333, 3.54166666666667, 4.58333333333333, 3.43750000000000, 0.625000000000000,
                    0.312500000000000, 2.29166666666667, 4.79166666666667, 2.81250000000000, 0.104166666666667, -0.208333333333,
                    -0.833333333333333, -0.416666666666667, 2.08333333333333, 5.31250000000000, 5.10416666666667, 1.04166666667,
                    -0.625000000000000, -0.104166666666667, 0.312500000000000]  # Spike shapes to be imposed

        mock_data = impose_template(noise=channel_noise, spikes=spikes, template=template)

        time_array[electrode] = mock_data[0]
        uv_data[electrode] = mock_data[1]

    raw_data = RAW_NeuronalData(uv_data=uv_data, input='RAWdata', time_array=time_array, channelids=channelids)

    return raw_data


def exponential_spike_generator():

    """ Generates spike data using a simple exponential-like random generator


          Returns:

             Spike times and total spike number
     """

    spikes = []
    num_cells = 1


    for i in range(num_cells):

        isi = np.random.exponential(size=300)  # Number of spikes
        spiketime = np.cumsum(isi)
        spiketime = spiketime.astype('int')
        spiketime = np.unique(spiketime)
        spikes.append(spiketime)

    spikenumber = len(spikes[0])  # List contains a single array

    print("Generated mock spiketimes.")

    return spikes, spikenumber


def impose_template(noise, spikes, template):

    """ Adds a template of a biological spike to given positions of a noise voltage array

           Arguments:

            noise(array): Noise of the channel
            spikes(array): Positions to add spike shapes
            template(list): Hard-coded

          Returns:

             Output file
     """

    print("Got into the impose function.")

    spike_number = len(spikes[0])

    recording_size = 5792501

    max_position = recording_size - 75

    imposed = noise[1]

    for firing in range(0, spike_number):

        spike_time = spikes[0][firing]

        position = spike_time * 25000

        if position < max_position:

            for voltage in range(0, 75):

                imposed[position + voltage] = template[voltage]

    return noise[0], imposed


def noise():

    """ # Generates channel noise using a Ornstein-Uhlenbeck process


         Returns:

             Duration array, voltage noise array and the channel threshold of -5.5 STDs.

           """

    print("Generating noise...")

    duration = np.linspace(0, 231, 5792501)  # 231 seconds, sampling rate of 25 kHz
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

    threshold = -5.5 * np.std(noise)

    print("Gata. Threshold of ", threshold)

    return duration, noise, threshold

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

        fig = plt.figure(dpi=500)

        ax = sns.lineplot(data=np.array(threshold_array[str(electrode)]))
        ax = sns.scatterplot(data=np.array(threshold_array[str(electrode)]))
        ax.set(title="MEA " + str(MEA) + " electrode " + str(electrode))
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

    fig = plt.figure(dpi=150)

    plt.plot(channeldata)

    plt.ylim(bottom=-70, top=30)
    plt.ylabel("Voltage (uV)")
    plt.xlim(left=0, right=6000000)
    plt.xlabel("Raw data points")

    plt.savefig(figpath + "Elec_" + str(channelnumber) + "_rd_" + str(recursiveround) + "_.png", format='png')
    plt.close(fig)


def plot_spike(voltage, occurrence, figpath, electrode, round):

    """ Plots a detected spike

          Arguments:

              voltage(list): Raw voltage data for a given electrode.
              occurrence(str): Spike number
              figpath(str): Where to plot the data (full path)

        Returns:

            Saved plot.

          """

    fig = plt.figure(dpi=500)

    ax = sns.lineplot(data=voltage)
    ax = sns.scatterplot(data=voltage)

    plt.title("Detected spike number " + str(occurrence))
    plt.ylim(bottom=-70, top=30)
    plt.ylabel("Voltage (uV)")
    plt.xlim(left=0, right=75)
    plt.xlabel("Data points")

    plt.savefig(figpath + "Elec_" + str(electrode) + "_rd_" + str(round) + "_spike_" + str(occurrence) + ".png", format='png')
    plt.close(fig)


def visualise_spikes_generated(output_path):

    """ Plots spike times generated with the custom exponential spike generator

             Arguments:

                 output_path(str): Full path of the output file

           Returns:

               Saved plot.

             """

    spikes = exponential_spike_generator()

    # Visualise #

    fig = plt.figure(dpi=500)

    filename = 'spikes'
    cells = [1]

    for cell in range(len(spikes[0])):

        plt.plot(spikes[cell], np.repeat(cells[cell], len(spikes[cell])), marker='o')

    plt.ylabel("Electrode number")
    plt.xlabel("Spike times")
    plt.title("Poisson Spiking")

    plt.savefig(output_path + filename + ".png", format='png')
    plt.close(fig)


def visualise_noise(output_path, noise, filename):

    """ Plots voltages generated with the custom noise generator

         Arguments:

             output_path(str): Full path of the output file
             noise(array): voltage array of the noise
             filename(str):  Filename of the output file

       Returns:

           Saved plot.

         """

    sns.set_palette(sns.dark_palette("purple"))

    ax = sns.lineplot(x=noise[0], y=noise[1])

    plt.savefig(output_path + filename + ".png", format='png')