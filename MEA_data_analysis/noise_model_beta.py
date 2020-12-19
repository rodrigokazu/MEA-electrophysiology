from class_RAW_NeuronalData import *
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.integrate import odeint

plt.rcParams.update({'font.size': 10})


def exponential_spike_generator():

    spikes = []
    num_cells = 1

    # Generates spike data using a simple Poisson-like generator #

    for i in range(num_cells):

        isi = np.random.exponential(size=100, scale=1.5)  # Number of spikes
        spiketime = np.cumsum(isi)
        spiketime = spiketime.astype('int')
        spiketime = np.unique(spiketime)
        spikes.append(spiketime)

    if spikes[0][0] == 0:

        spikes[0] = np.delete(spikes[0], 0)

    spikenumber = len(spikes[0])  # List contains a single array

    print("Generated mock spiketimes.")

    return spikes, spikenumber


def noise():

    # Generates channel noise using a Ornstein-Uhlenbeck process #

    print("Generating noise...")

    duration = np.linspace(0, 231, 5792501)  # 231 seconds, sampling rate of 25 kHz
    N = len(duration)
    noise = np.zeros(N)
    h = duration[1] - duration[0]
    tau = 0.5
    Xrest = 0
    Xthres = -10
    noise[0] = Xrest

    I = lambda t: 0.0

    for i in range(N-1):

        noise[i + 1] = noise[i] - h*(noise[i] - Xrest)/tau + np.sqrt(h)*np.random.normal(scale=5.0) + I(duration)

    threshold = -5.5 * np.std(noise)

    print("Gata. Threshold of ", threshold)

    return duration, noise, threshold


def visualise_noise(output_path, duration, noise, filename):

    fig = plt.figure(dpi=500)

    #sns.set_palette(sns.dark_palette("purple"))

    #ax = sns.lineplot(x=duration, y=noise)

    plt.plot(duration, noise)

    plt.ylim([-62, 22])
    plt.ylabel("Microvolts")
    plt.xlabel("Seconds")
    plt.title("Mock recording")

    plt.savefig(output_path + filename + ".png", format='png')
    plt.close(fig)


def impose_template(noise, spikes, template, template_small):

    print("Got into the impose function.")

    spike_number = len(spikes[0][0])

    recording_size = 5792501

    max_position = recording_size - 75

    imposed = noise[1]

    halfway = spike_number/2

    halfway = int(halfway)

    for firing in range(0, halfway):

        print("Imposing larger amplitude spike number.", firing)

        spike_time = spikes[0][0][firing]

        position = spike_time * 25000

        if 25 < position < max_position:

            for voltage in range(0, 25):  # Part of the spike that precedes the apex

                imposed[position - voltage] = template[25 - voltage]

            for voltage in range(0, 50):  # Part of the spike that follows the apex

                imposed[position + voltage] = template[25 + voltage]

    for firing in range(halfway, spike_number):

        print("Imposing smaller amplitude spike number.", firing)

        spike_time = spikes[0][0][firing]

        position = spike_time * 25000

        if 25 < position < max_position:

            for voltage in range(0, 25):  # Part of the spike that precedes the apex

                imposed[position - voltage] = template_small[25 - voltage]

            for voltage in range(0, 50):  # Part of the spike that follows the apex

                imposed[position + voltage] = template_small[25 + voltage]

    print("Finished with the spikes")

    return noise[0], imposed


def create_mockdata(output_path, electrode):

    uv_data = {}
    time_array = {}
    channelids = {}

    channels = list()
    channels.append(str(electrode))

    fullname = output_path + "Mock_" + str(electrode) + ".txt"
    file = open(fullname, "w+")

    template = [1.77083333333333, 1.04166666666667, 1.97916666666667, 2.81250000000000, 1.87500000000000,
                1.56250000000000,
                2.70833333333333, 2.81250000000000, 3.12500000000000, 3.33333333333333, 2.50000000000000,
                1.14583333333333,
                1.77083333333333, 2.50000000000000, 0.937500000000000, 0.729166666666667, 1.66666666666667,
                2.500000000000,
                1.35416666666667, 1.97916666666667, 5.93750000000000, 12.5000000000000, 18.5416666666667,
                18.4375000000000,
                4.16666666666667, -29.6666666666667, -39.7916666666667, -59, -41.4583333333333, -25.5000000000000,
                -17.2916666666667, -14.5833333333333, -10.8333333333333, -8.22916666666667, -6.77083333333333,
                -3.12500000,
                -2.18750000000000, -1.45833333333333, -0.937500000000000, 0.104166666666667, 3.02083333333333,
                2.2916666667,
                0.416666666666667, 0.625000000000000, 2.91666666666667, 3.22916666666667, 3.75000000000000,
                6.1458333333333,
                6.56250000000000, 6.97916666666667, 6.04166666666667, 5.41666666666667, 5.10416666666667,
                5.10416666666667,
                6.66666666666667, 5.52083333333333, 3.54166666666667, 4.58333333333333, 3.43750000000000,
                0.625000000000000,
                0.312500000000000, 2.29166666666667, 4.79166666666667, 2.81250000000000, 0.104166666666667,
                -0.208333333333,
                -0.833333333333333, -0.416666666666667, 2.08333333333333, 5.31250000000000, 5.10416666666667,
                1.04166666667,
                -0.625000000000000, -0.104166666666667, 0.312500000000000]  # Spike shapes to be imposed

    template_small = [1.77083333333333, 1.04166666666667, 1.97916666666667, 2.81250000000000, 1.87500000000000,
                      1.56250000000000,
                      2.70833333333333, 2.81250000000000, 3.12500000000000, 3.33333333333333, 2.50000000000000,
                      1.14583333333333,
                      1.77083333333333, 2.50000000000000, 0.937500000000000, 0.729166666666667, 1.66666666666667,
                      2.500000000000,
                      1.35416666666667, 1.97916666666667, 5.93750000000000, 12.5000000000000, 18.5416666666667,
                      18.4375000000000,
                      4.16666666666667, -12.6666666666667, -22, -28.75, -24, -19.5000000000000,
                      -17.2916666666667, -14.5833333333333, -10.8333333333333, -8.22916666666667, -6.77083333333333,
                      -3.12500000,
                      -2.18750000000000, -1.45833333333333, -0.937500000000000, 0.104166666666667, 3.02083333333333,
                      2.2916666667,
                      0.416666666666667, 0.625000000000000, 2.91666666666667, 3.22916666666667, 3.75000000000000,
                      6.1458333333333,
                      6.56250000000000, 6.97916666666667, 6.04166666666667, 5.41666666666667, 5.10416666666667,
                      5.10416666666667,
                      6.66666666666667, 5.52083333333333, 3.54166666666667, 4.58333333333333, 3.43750000000000,
                      0.625000000000000,
                      0.312500000000000, 2.29166666666667, 4.79166666666667, 2.81250000000000, 0.104166666666667,
                      -0.208333333333,
                      -0.833333333333333, -0.416666666666667, 2.08333333333333, 5.31250000000000, 5.10416666666667,
                      1.04166666667,
                      -0.625000000000000, -0.104166666666667, 0.312500000000000]

    for electrode in channels:

        channelids[electrode] = list()

        channel_noise = noise()  # Creates noise for the channel
        # channel_noise = zeros() # Replace noises with an array of zeros if needed

        Threshold_noise = "Noise threshold for" + str(electrode) + "=" + str(channel_noise[2])

        file.write(Threshold_noise)

        file.write("\n")

        spikes = exponential_spike_generator()  # Randomly generated spike times

        time_array['mock_spiketimes'] = spikes

        Mock_electrode_spiketimes = "Spike times for" + str(electrode) + "=" + str(spikes[0][0])

        file.write(Mock_electrode_spiketimes)

        file.write("\n")

        Mock_electrode_detections = "Spike number for" + str(electrode) + "=" + str(spikes[1])

        file.write(Mock_electrode_detections)

        file.write("\n")

        file.close()

        # mock_data = channel_noise # Uncomment this and comment next line to run detection only on the noise
        mock_data = impose_template(noise=channel_noise, spikes=spikes, template=template, template_small=template_small)

        time_array[electrode] = mock_data[0]
        uv_data[electrode] = mock_data[1]

    raw_data = RAW_NeuronalData(uv_data=uv_data, input='RAWdata', time_array=time_array, channelids=channelids)

    return raw_data


def mockdata_60elecs(output_path):

    mockMEA = {}

    for electrode in range(0, 60):

        mockMEA[electrode] = create_mockdata(electrode=str(electrode), output_path=output_path)

        visualise_noise(output_path=output_path, duration=np.array(mockMEA[electrode].mcd_data['ms']),
                        noise=np.array(mockMEA[electrode].mcd_data[str(electrode)]),
                        filename="Original_mock_data" + str(electrode))

        print('RAW_NeuronalData object for ', electrode, ' created at ', time.asctime(time.localtime(time.time())))

        # Filtering #

        #mockMEA[electrode] = mockMEA[electrode].bandstop_resonator()

        #visualise_noise(output_path=output_path, duration=np.array(mockMEA[electrode].mcd_data['ms']),
        #                noise=np.array(mockMEA[electrode].mcd_data[str(electrode)]),
        #                filename="Bandstop_mock"+str(electrode))

        #mockMEA[electrode] = mockMEA[electrode].highpass()

        #visualise_noise(output_path=output_path, noise=mockMEA[electrode].mcd_data[str(electrode)],
        #                filename="Highpass_mock"+str(electrode))

        #print('Data filtered (20Hz High Pass and 50Hz bandstop resonator (notch) at',
        #      time.asctime(time.localtime(time.time())))

        # Detecting #

        spikes_detected = mockMEA[electrode].recursive_spike_detection(MEA='Synthetic'+str(electrode), figpath=output_path)
        spikes_detected.number_of_detections(filename="Mock_electrode_"+str(electrode), output_path=output_path)

        del spikes_detected


def zeros():

    zero = np.zeros(5792501)
    duration = np.linspace(0, 231, 5792501)  # 231 seconds, sampling rate of 25 kHz
    threshold = -5.5 * np.std(zero)

    return duration, zero, threshold


def highpass_test(dataset):

    """ Creates a Butterworth filter with a cutoff of 0.02 times the Nyquist rate, or 20 Hz and runs it through a
    RAW_NeuronalData object with sampling rate of 25000000 milisamples per second, 25000 Hz.

            Arguments:

                RAW_NeuronalData object

            Returns:

               Filtered RAW_NeuronalData object
            """

    nyq = 0.5 * 25000
    normal_cutoff = 300 / nyq
    b, a = signal.butter(N=3, Wn=normal_cutoff, btype='highpass', analog=False)

    filtered = signal.filtfilt(b, a, dataset[1])

    return dataset[0], filtered

smaller_noise = noise()

path_zero = "C:\\Users\\Admin\\Dropbox\\PhD\\Thesis\\Analysis_Pipeline\\Ephys quantification\\" \
            "Recursive analysis outputs\\Validation plots\\Mock data\\Plots\\Noise_play\\"

visualise_noise(output_path=path_zero, duration=smaller_noise[0], noise=smaller_noise[1],
                filename="Smaller_noise_Mar22")

smaller_noise = highpass_test(smaller_noise)

visualise_noise(output_path=path_zero, duration=smaller_noise[0], noise=smaller_noise[1],
                filename="Smaller_noise_Mar22_filtered300")

