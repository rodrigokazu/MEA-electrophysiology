import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
import pandas as pd

validation_dict = dict()

validation_dict['Synthetic spikes'] = [73, 70, 74, 77, 74, 75, 71, 76, 72, 77, 73, 71, 71, 75, 64, 71, 68, 75, 75, 68,
                                       70, 80, 74, 73, 73, 73, 70, 73, 70, 73, 81, 71, 61, 81, 77, 71, 69, 75, 73, 75,
                                       70, 74, 76, 63, 77, 74, 77, 75, 78, 68]

validation_dict['Detected spikes'] = [73, 70, 74, 77, 74, 75, 71, 76, 72, 77, 73, 71, 71, 75, 64, 71, 68, 75, 75, 68,
                                       70, 80, 74, 73, 73, 73, 70, 73, 70, 73, 81, 71, 61, 81, 77, 71, 69, 75, 73, 75,
                                       70, 74, 76, 63, 77, 74, 77, 75, 78, 68]

outputpath = "C:\\Users\\Admin\\Dropbox\\PhD\\Thesis\\Analysis_Pipeline\\Ephys quantification" \
             "\\Recursive analysis outputs\\Validation plots\\"

# Computes the fraction of spikes being detected and writes it to a file #

synt = np.array(validation_dict['Synthetic spikes'])

meansynt = np.mean(synt)

detec = np.array(validation_dict['Detected spikes'])

meandetec = np.mean(detec)

division = np.divide(detec, synt)

mean = np.mean(division)

ttest = stats.ttest_ind(synt, detec, equal_var=False)

p = ttest[1]

print("P value of ", p)

percentage = mean * 100

averagedetection = "In average " + str(percentage) + " percent of all spikes was detected."

fullname = outputpath + "Validation_50elecs_twoshapes.txt"
file = open(fullname, "w+")

file.write(averagedetection)

file.close()

# Plots the dataset #

dataframe = pd.DataFrame(validation_dict)

fig = plt.figure(dpi=500)

ax = sns.barplot(data=dataframe, ci='sd', palette='cividis')
ax = sns.swarmplot(data=dataframe, palette='Greys')
ax.set(ylim=[0, 100], ylabel="Number of spikes")

plt.savefig(outputpath+"Detectedspikes_50elecs_twoshapes.png", format='png')

plt.show()

"""

# Single spike shape introducted # 

validation_dict['Synthetic spikes'] = [69, 77, 75, 78, 77, 66, 70, 69, 77, 74, 81, 79, 67, 78, 65, 74, 71, 76, 67, 71,
                                       72, 69, 66, 73, 71, 78, 68, 75, 73, 70, 75, 71, 77, 73, 76, 71, 73, 68, 70, 74,
                                       72, 73, 76, 77, 73, 68, 68, 73, 71, 73]

validation_dict['Detected spikes'] = [69, 77, 75, 78, 77, 66, 70, 69, 77, 74, 81, 79, 67, 78, 65, 74, 71, 76, 67, 71,
                                       72, 69, 66, 73, 71, 78, 68, 75, 73, 70, 75, 71, 77, 73, 76, 71, 73, 68, 70, 74,
                                       72, 73, 76, 77, 73, 68, 68, 73, 71, 73]
                                       
"""