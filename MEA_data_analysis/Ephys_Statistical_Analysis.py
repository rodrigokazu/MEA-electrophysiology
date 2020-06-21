import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as stats
import io
from statsmodels.stats.libqsturng import psturng
from statsmodels.stats.multicomp import pairwise_tukeyhsd, MultiComparison
from statannot import add_stat_annotation

#plt.rc('xtick', labelsize=4)
plt.rcParams.update({'font.size': 14})

# Function definitions #


def active_cultures(cultures_path, filename, outputpath, scaling, title, ytitle, ymax):

    CultureNumber_df = pd.read_excel(cultures_path)

    CultureNumber_df = CultureNumber_df.transpose()

    fig = plt.figure(dpi=500)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)},  font_scale=scaling)
    ax = sns.barplot(data=CultureNumber_df, palette='cividis')
    # ax = sns.swarmplot(data=CultureNumber_df, palette='Greys_r')
    ax.set(title=title, ylabel=ytitle, ylim=[0, ymax])

    plt.savefig(outputpath + filename + "active_cultures_comparison.png", format='png')


def active_electrodes_comparison(DIVs_df, filename, outputpath, scaling, title):

    active_electrodes = pd.DataFrame()

    for DIV in DIVs_df:

        active_electrodes[DIV] = DIVs_df[DIV]['Individual_Active_Elecs']

    pvalues = oneway_ANOVA_plusTukeyHSD(DIVs_dataframe=active_electrodes, dropzero='y',
                                        file_name=filename+"Elec_comparison", outputpath=outputpath)

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)},  font_scale=scaling)
    ax = sns.barplot(data=active_electrodes, palette='cividis')
    ax = sns.swarmplot(data=active_electrodes, palette='Greys_r')

    add_stat_annotation(ax, data=active_electrodes, text_format='star', loc='inside', verbose=2, linewidth=3,
                        box_pairs=[("DIV14", "DIV21"), ("DIV14", "DIV7"), ("DIV21", "DIV7")], perform_stat_test=False,
                        test=None, line_offset=0.3, line_offset_to_box=0.3, pvalues=pvalues)

    ax.set(title="Number of active electrodes over time" + title, ylabel="Active electrodes", ylim=[-0.1, 60])

    plt.savefig(outputpath + filename + "active_electrodes_comparison.png", format='png')


def burst_comparison(DIVs_df, filename, outputpath, title, ymax):

    active_electrodes = pd.DataFrame()

    for DIV in DIVs_df:

        active_electrodes[DIV] = DIVs_df[DIV]['Individual_Burst_Counts']

    pvalues = oneway_ANOVA_plusTukeyHSD(DIVs_dataframe=active_electrodes, dropzero='n', file_name=filename+"Burst_comparison", outputpath=outputpath)

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)},  font_scale=1.75)
    ax = sns.barplot(data=active_electrodes, palette='cividis')
    ax = sns.swarmplot(data=active_electrodes, palette='Greys_r')
    add_stat_annotation(ax, data=active_electrodes, text_format='star', loc='inside', verbose=2, linewidth=3,
                        box_pairs=[("DIV14", "DIV21"), ("DIV14", "DIV7"), ("DIV21", "DIV7")], perform_stat_test=False,
                        test=None, line_offset=0.05, pvalues=pvalues)
    ax.set(title="Temporal evolution of Burst counts" + title, ylabel="Number of bursts", ylim=[-0.1, ymax])

    plt.savefig(outputpath + filename + "bursts_comparison_overtime.png", format='png')


def dataframe_generation(DIV_paths):

    DIVs_df = dict()

    for DIV in DIV_paths:

        DIVs_df[DIV] = pd.read_excel(DIV_paths[DIV])

    return DIVs_df


def FR_comparison(DIVs_df, filename, offset, outputpath, title, scaling, ymax):

    active_electrodes = pd.DataFrame()

    for DIV in DIVs_df:

        active_electrodes[DIV] = DIVs_df[DIV]['Individual_FRs']

    pvalues = oneway_ANOVA_plusTukeyHSD(DIVs_dataframe=active_electrodes, dropzero='n', file_name=filename+"FR_comparison_", outputpath=outputpath)

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)},  font_scale=scaling)
    ax = sns.barplot(data=active_electrodes, palette='cividis')
    ax = sns.swarmplot(data=active_electrodes, palette='Greys_r')
    add_stat_annotation(ax, data=active_electrodes, text_format='star', loc='inside', verbose=2, linewidth=3,
                        box_pairs=[("DIV14", "DIV21"), ("DIV14", "DIV7"), ("DIV21", "DIV7")], perform_stat_test=False,
                        test=None, line_offset=offset, line_offset_to_box=0.3, pvalues=pvalues)
    ax.set(title="Temporal evolution of firing rates" + title, ylabel="Firing rate (Hz)", ylim=[-0.02, ymax])

    plt.savefig(outputpath + filename + "FR_comparison_overtime.png", format='png')


def ISI_comparison(DIVs_df, filename, offset, outputpath, title, scaling, ymax):

    active_electrodes = pd.DataFrame()

    for DIV in DIVs_df:

        active_electrodes[DIV] = DIVs_df[DIV]['Individual_ISI']

    pvalues = oneway_ANOVA_plusTukeyHSD(DIVs_dataframe=active_electrodes, dropzero='y', file_name=filename+"ISI_comparison_",
                              outputpath=outputpath)

    fig = plt.figure(dpi=700)

    sns.set_context("talk")
    sns.set(rc={'figure.figsize': (10, 10)},  font_scale=scaling)
    ax = sns.barplot(data=active_electrodes, palette='cividis')
    ax = sns.swarmplot(data=active_electrodes, palette='Greys_r')

    add_stat_annotation(ax, data=active_electrodes, text_format='star', loc='inside', verbose=2, linewidth=3,
                        box_pairs=[("DIV14", "DIV21"), ("DIV14", "DIV7"), ("DIV21", "DIV7")], perform_stat_test=False,
                        test=None, line_offset=offset, line_offset_to_box=0.15, pvalues=pvalues)

    ax.set(title="Temporal evolution of ISIs" + title, ylabel="ISI (ms)", ylim=[-0.05, ymax])

    plt.savefig(outputpath + filename + "ISIs_comparison_overtime.png", format='png')


def oneway_ANOVA_plusTukeyHSD(DIVs_dataframe, dropzero, file_name, outputpath):

    """ Runs a one-way ANOVA with a post-hoc test (Tukey HSD)

           Arguments:

            DIVs_dataframe(dict): Dictionary with the data to be tested (DIVs as column titles)
            dropzero(char): 'y' or 'n' to remove the zeros of the dataset
            file_name(str): Prefix of name on the file to be saved.
            output_path(str): Full path of the output file

          Returns:

             pvalues list and ANOVA summary in a txt file

          """

    # Dropping NaNs

    NaNfree = [DIVs_dataframe[col].dropna() for col in DIVs_dataframe]

    if dropzero == 'y':

        # Dropping zeros

        DIVs_dataframe['DIV7'] = DIVs_dataframe['DIV7'][DIVs_dataframe['DIV7'] > 0]
        DIVs_dataframe['DIV14'] = DIVs_dataframe['DIV14'][DIVs_dataframe['DIV14'] > 0]
        DIVs_dataframe['DIV21'] = DIVs_dataframe['DIV21'][DIVs_dataframe['DIV21'] > 0]

    # Running the ANOVA per se

    fvalue, pvalue = stats.f_oneway(*NaNfree)

    print("F =", fvalue)
    print("p =", pvalue)
    ANOVAresults = "\n" + str(fvalue) + " " + str(pvalue) + "\n\n"

    # Post-hoc tests after stacking the data

    stacked_data = DIVs_dataframe.stack().reset_index()
    stacked_data = stacked_data.rename(columns={'level_0': 'id', 'level_1': 'DIV', 0: 'value'})

    MultiComp = MultiComparison(stacked_data['value'].astype('float'), stacked_data['DIV'])

    res = MultiComp.tukeyhsd()  # Results of the Tukey HSD

    # Exporting results

    summary = res.summary()
    summary = summary.as_text()  # ANOVA summary

    buffer = io.StringIO()
    DIVs_dataframe.info(buf=buffer)
    info = buffer.getvalue()  # Dataset info

    mean = str(DIVs_dataframe.mean(axis=0))
    std = str(DIVs_dataframe.std(axis=0))
    pvalues = psturng(np.abs(res.meandiffs / res.std_pairs), len(res.groupsunique), res.df_total)

    file = open(outputpath + file_name + "_ANOVA.txt", "w+")

    file.write("Means of the dataset: \n")
    file.write(mean)
    file.write("\n \nSTD of the dataset: \n")
    file.write(std)
    file.write("\n \nRelevant info of the dataset: \n")
    file.write(info)
    file.write("\n \nF-value and overall p-value: \n")
    file.write(ANOVAresults)  # ANOVA results
    file.write(summary)  # ANOVA summary
    file.write("\n \np-values: \n")
    file.write(str(pvalues))

    file.close()

    return pvalues


print("\nBrain Embodiment Laboratory at the University of Reading \nStatistical analysis of Ephys Results from Kazu, "
      "R.S. thesis, 2020. \nPlease change your filepath inside the code. \n")

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

"""

DIV7_MClow = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
           '\\Low-density\\MC_DIV_Analysis_Output.xlsx'

DIV7_MCmid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
           '\\Mid-density\\MC_DIV_Analysis_Output.xlsx'

DIV7_MChigh = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV7' \
            '\\High-density\\MC_DIV_Analysis_Output.xlsx'
            
"""

# DIV 14

DIV14_MCpath = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\DIV14' \
             '\\MC_DIV_Analysis_Output.xlsx'

"""

DIV14_MClow = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
            '\\Low-density\\MC_DIV_Analysis_Output.xlsx'

DIV14_MCmid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
            '\\Mid-density\\MC_DIV_Analysis_Output.xlsx'

DIV14_MChigh = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV14' \
             '\\High-density\\MC_DIV_Analysis_Output.xlsx'
            
"""

# DIV 21

DIV21_MCpath = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per DIV\\DIV21' \
             '\\MC_DIV_Analysis_Output.xlsx'

"""

DIV21_MClow = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\Low-density\\MC_DIV_Analysis_Output.xlsx'

DIV21_MCmid = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\Mid-density\\MC_DIV_Analysis_Output.xlsx'

DIV21_MChigh = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\DIV21' \
            '\\High-density\\MC_DIV_Analysis_Output.xlsx'
            
"""

# Saving locations

outputpath = 'C:\\Users\\pc1rss\\Dropbox\\PhD\\Backup_Experimental_Data\\Ephys_data_with_mats\\Per density\\'

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

"""

Low_MCdensity = {"DIV7": DIV7_MClow, "DIV14": DIV14_MClow, "DIV21": DIV21_MClow}

Mid_MCdensity = {"DIV7": DIV7_MCmid, "DIV14": DIV14_MCmid, "DIV21": DIV21_MCmid}

High_MCdensity = {"DIV7": DIV7_MChigh, "DIV14": DIV14_MChigh, "DIV21": DIV21_MChigh}

"""

# Analysis block #

# Generating the dataframes per day in vitro of experiment #

DIVs_df = dataframe_generation(DIV_paths)

DIVs_MCdf = dataframe_generation(DIV_MCpaths)

# Generating the dataframes per cellular density #

Low_df = dataframe_generation(Low_density)

Mid_df = dataframe_generation(Mid_density)

High_df = dataframe_generation(High_density)


# Generating the plots for the percentage of active cultures overt time and condition #

active_cultures(cultures_path=NumberofCultures_xlsx, filename="Over_condition_",
                title="Percentage of active cultures per condition", ytitle="Percentage of active cultures",
                ymax=100, outputpath=Ephys_path, scaling=1)

active_cultures(cultures_path=Ncultures_overtime_xlsx, filename="Over_time_",
                title="Number of active cultures per DIV", ytitle="Number of active cultures",
                ymax=40, outputpath=Ephys_path, scaling=2)


# Creating the active electrodes plots with stats #

active_electrodes_comparison(DIVs_df=DIVs_df, filename='Recur_', outputpath=Ephys_path, scaling=2,
                             title=" for all cultures.")


active_electrodes_comparison(DIVs_df=Low_df, filename='Low-density_', outputpath=outputpath,  scaling=1.7,
                             title=" for low-density cultures.")


active_electrodes_comparison(DIVs_df=Mid_df, filename='Mid-density_', outputpath=outputpath, scaling=1.7,
                             title=" for mid-density cultures.")

active_electrodes_comparison(DIVs_df=High_df, filename='High-density_', outputpath=outputpath, scaling=1.7,
                             title=" for high-density cultures.")

# active_electrodes_comparison(DIVs_df=DIVs_MCdf, filename='MC', outputpath=outputpath)

# Creating the Firing Rates (Hz) plots with stats #

FR_comparison(DIVs_df=DIVs_df, filename='Recur_', offset=0.1, outputpath=Ephys_path, title=" for all cultures.",
              scaling=1, ymax=20)

FR_comparison(DIVs_df=Low_df, filename='Low-density_', offset=0.1, outputpath=outputpath, title=" for low-density cultures.",
              scaling=1.75, ymax=20)

FR_comparison(DIVs_df=Mid_df, filename='Mid-density_', offset=0.3, outputpath=outputpath,
              title=" for medium-density cultures.", scaling=1.75, ymax=5)

FR_comparison(DIVs_df=High_df, filename='High-density_', offset=0.5, outputpath=outputpath,
              title=" for high-density cultures.", scaling=1.75, ymax=5)

# Creating the Burst count plots with stats #

burst_comparison(DIVs_df=DIVs_df, filename='Recur_', outputpath=Ephys_path, title=" for all cultures.", ymax=100)

burst_comparison(DIVs_df=Low_df, filename='Low-density_', outputpath=outputpath, title=" for low-density cultures.",
                 ymax=100)

burst_comparison(DIVs_df=Mid_df, filename='Mid-density_', outputpath=outputpath, title=" for mid-density cultures.",
                 ymax=60)

burst_comparison(DIVs_df=High_df, filename='High-density_', outputpath=outputpath, title=" for high-density cultures.",
                 ymax=60)

# Creating the comparative ISIs plots without stats #

ISI_comparison(DIVs_df=DIVs_df, filename='Recur_', offset=0.1, outputpath=Ephys_path, title=" for all cultures.",
               scaling=1.2, ymax=20000)

ISI_comparison(DIVs_df=Low_df, filename='Low-density_', offset=0.1, outputpath=outputpath, title=" for low-density cultures.",
               scaling=2, ymax=15000)

ISI_comparison(DIVs_df=Mid_df, filename='Mid-density_', offset=0.3, outputpath=outputpath, title=" for mid-density cultures.",
               scaling=2, ymax=6000)

ISI_comparison(DIVs_df=High_df, filename='High-density_', offset=0.3, outputpath=outputpath, title=" for high-density cultures.",
               scaling=2, ymax=6000)

