import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
#from statannot import add_stat_annotation

# Function definitions #

def active_cultures(cultures_path, filename, outputpath, ymax):

    CultureNumber_df = pd.read_excel(cultures_path)

    CultureNumber_df = CultureNumber_df.transpose()

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)})
    ax = sns.barplot(data=CultureNumber_df, palette='cividis')
    # ax = sns.swarmplot(data=CultureNumber_df, palette='Greys_r')
    ax.set(title="Percentage of active cultures per condition", ylabel="Active cultures", ylim=[0, ymax])

    plt.savefig(outputpath + filename + "active_cultures_comparison.png", format='png')


def active_electrodes_comparison(DIVs_df, filename, outputpath):

    active_electrodes = pd.DataFrame()

    for DIV in DIVs_df:

        active_electrodes[DIV] = DIVs_df[DIV]['Individual_Active_Elecs']

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)})
    ax = sns.barplot(data=active_electrodes, palette='cividis')
    ax = sns.swarmplot(data=active_electrodes, palette='Greys_r')
    ax.set(title="Temporal evolution of MEA active electrodes", ylabel="Active electrodes", ylim=[0, 35])

    plt.savefig(outputpath + filename + "active_electrodes_comparison.png", format='png')


def burst_comparison(DIVs_df, filename, outputpath, ymax):

    active_electrodes = pd.DataFrame()

    for DIV in DIVs_df:

        active_electrodes[DIV] = DIVs_df[DIV]['Individual_Burst_Counts']

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)})
    ax = sns.barplot(data=active_electrodes, palette='cividis')
    ax = sns.swarmplot(data=active_electrodes, palette='Greys_r')
    ax.set(title="Temporal evolution of Burst counts", ylabel="Number of bursts", ylim=[-0.05, ymax])

    plt.savefig(outputpath + filename + "bursts_comparison_overtime.png", format='png')


def dataframe_generation(DIV_paths):

    DIVs_df = dict()

    for DIV in DIV_paths:

        DIVs_df[DIV] = pd.read_excel(DIV_paths[DIV])

    return DIVs_df


def FR_comparison(DIVs_df, filename, outputpath):

    active_electrodes = pd.DataFrame()

    for DIV in DIVs_df:

        active_electrodes[DIV] = DIVs_df[DIV]['Individual_FRs']

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)})
    ax = sns.barplot(data=active_electrodes, palette='cividis')
    ax = sns.swarmplot(data=active_electrodes, palette='Greys_r')
    ax.set(title="Temporal evolution of firing rates", ylabel="Firing rate (Hz)", ylim=[-0.05, 12])

    plt.savefig(outputpath + filename + "FR_comparison_overtime.png", format='png')


def ISI_comparison(DIVs_df, filename, outputpath, ymax):

    active_electrodes = pd.DataFrame()

    for DIV in DIVs_df:
        active_electrodes[DIV] = DIVs_df[DIV]['Individual_ISI']

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)})
    ax = sns.barplot(data=active_electrodes, palette='cividis')
    ax = sns.swarmplot(data=active_electrodes, palette='Greys_r')
    ax.set(title="Temporal evolution of Interspike Intervals", ylabel="ISI (ms)", ylim=[-0.05, ymax])

    plt.savefig(outputpath + filename + "ISIs_comparison_overtime.png", format='png')


print("\nBrain Embodiment Laboratory at the University of Reading \nStatistical analysis of Ephys Results from Kazu, "
      "R.S. thesis, 2020. \n Please change your filepath inside the code. \n")

# PATHs block #
# MC paths are the paths of recordings where spike detection happened inside MC_Rack #

# DIV 7

DIV7_path = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\DIV7' \
            '\\DIV_Analysis_Output.xlsx'

DIV7_low = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
           '\\Low-density\\DIV_Analysis_Output.xlsx'

DIV7_mid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
           '\\Mid-density\\DIV_Analysis_Output.xlsx'

DIV7_high = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
            '\\High-density\\DIV_Analysis_Output.xlsx'

# DIV 14

DIV14_path = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\DIV14' \
             '\\DIV_Analysis_Output.xlsx'

DIV14_low = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
            '\\Low-density\\DIV_Analysis_Output.xlsx'

DIV14_mid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
            '\\Mid-density\\DIV_Analysis_Output.xlsx'

DIV14_high = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
             '\\High-density\\DIV_Analysis_Output.xlsx'

# DIV 21

DIV21_path = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\DIV21' \
             '\\DIV_Analysis_Output.xlsx'

DIV21_low = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\Low-density\\DIV_Analysis_Output.xlsx'

DIV21_mid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\Mid-density\\DIV_Analysis_Output.xlsx'

DIV21_high = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\High-density\\DIV_Analysis_Output.xlsx'

# MC rack detected

# DIV 7

DIV7_MCpath = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\DIV7' \
            '\\MC_DIV_Analysis_Output.xlsx'

DIV7_MClow = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
           '\\Low-density\\MC_DIV_Analysis_Output.xlsx'

DIV7_MCmid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
           '\\Mid-density\\MC_DIV_Analysis_Output.xlsx'

DIV7_MChigh = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
            '\\High-density\\MC_DIV_Analysis_Output.xlsx'

# DIV 14

DIV14_MCpath = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\DIV14' \
             '\\MC_DIV_Analysis_Output.xlsx'

DIV14_MClow = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
            '\\Low-density\\MC_DIV_Analysis_Output.xlsx'

DIV14_MCmid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
            '\\Mid-density\\MC_DIV_Analysis_Output.xlsx'

DIV14_MChigh = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
             '\\High-density\\MC_DIV_Analysis_Output.xlsx'

# DIV 21

DIV21_MCpath = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\DIV21' \
             '\\MC_DIV_Analysis_Output.xlsx'

DIV21_MClow = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\Low-density\\MC_DIV_Analysis_Output.xlsx'

DIV21_MCmid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\Mid-density\\MC_DIV_Analysis_Output.xlsx'

DIV21_MChigh = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\High-density\\MC_DIV_Analysis_Output.xlsx'

# Saving locations

outputpath = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\'

Ephys_path = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Thesis\\Analysis_Pipeline\\Ephys quantification\\'

# Active cultures per condition dataframe #

NumberofCultures_xlsx = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Thesis\\Analysis_Pipeline\\Ephys quantification' \
                        '\\Excel files\\Active_MEAs_percentage.xlsx'

Ncultures_overtime_xlsx = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Thesis\\Analysis_Pipeline\\Ephys quantification' \
                        '\\Excel files\\Active_MEAs_overtime.xlsx'

# Dictionaries of paths from the recursive spike detection #

DIV_paths = {"DIV7": DIV7_path, "DIV14": DIV14_path, "DIV21": DIV21_path}

Low_density = {"DIV7": DIV7_low, "DIV14": DIV14_low, "DIV21": DIV21_low}

Mid_density = {"DIV7": DIV7_mid, "DIV14": DIV14_mid, "DIV21": DIV21_mid}

High_density = {"DIV7": DIV7_high, "DIV14": DIV14_high, "DIV21": DIV21_high}

# Dictionaries of paths from the MC_Rack spike detection #

DIV_MCpaths = {"DIV7": DIV7_MCpath, "DIV14": DIV14_MCpath, "DIV21": DIV21_MCpath}

Low_MCdensity = {"DIV7": DIV7_MClow, "DIV14": DIV14_MClow, "DIV21": DIV21_MClow}

Mid_MCdensity = {"DIV7": DIV7_MCmid, "DIV14": DIV14_MCmid, "DIV21": DIV21_MCmid}

High_MCdensity = {"DIV7": DIV7_MChigh, "DIV14": DIV14_MChigh, "DIV21": DIV21_MChigh}

# Analysis block #

# Generating the dataframes per day in vitro of experiment #

DIVs_df = dataframe_generation(DIV_paths)

#DIVs_MCdf = dataframe_generation(DIV_MCpaths)

# Generating the plots for the percentage of active cultures overt time and condition #

active_cultures(cultures_path=NumberofCultures_xlsx, filename="Over_condition_", ymax=100, outputpath=Ephys_path)

active_cultures(cultures_path=Ncultures_overtime_xlsx, filename="Over_time_", ymax=40, outputpath=Ephys_path)

# Creating the active electrodes plots without stats #

active_electrodes_comparison(DIVs_df=DIVs_df, filename='Recur_', outputpath=outputpath)

#active_electrodes_comparison(DIVs_df=DIVs_MCdf, filename='MC', outputpath=outputpath)

# Creating the Firing Rates (Hz) plots without stats #

FR_comparison(DIVs_df=DIVs_df, filename='Recur_', outputpath=Ephys_path)

# Creating the Burst count plots without stats #

burst_comparison(DIVs_df=DIVs_df, filename='Recur_', outputpath=Ephys_path, ymax=60)

# Creating the comparative ISIs plots without stats #

ISI_comparison(DIVs_df=DIVs_df, filename='Recur_', outputpath=Ephys_path, ymax=15000)
