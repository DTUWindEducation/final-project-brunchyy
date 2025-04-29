Wind Direction Bins (dir_bin): Groups wind direction into 12 bins (each covering 30°).

import numpy as np
import matplotlib.pyplot as plt

# Group by direction bin and compute mean wind speed
DirBinProps = WindData.groupby('dir_bin').mean() # wind_direction_100m

# Ensure the index is numeric
DirBinProps = DirBinProps.sort_index()

# Convert direction bin to radians (each bin represents 30 degrees)
angles = np.deg2rad(DirBinProps.index * 30)

# Wind speeds in each bin
wind_speeds = DirBinProps['Wsp_18m'] # wind_speed_100m

# Create polar plot
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})

# Plot wind speeds against direction bins
ax.bar(angles, wind_speeds, width=np.deg2rad(30), bottom=0, alpha=0.6, color='b', edgecolor='k')

# Set labels
ax.set_theta_zero_location('N')  # Set 0° (North) at the top
ax.set_theta_direction(-1)  # Set clockwise direction

# Define the direction labels (12 bins of 30 degrees)
direction_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
ax.set_xticks(np.linspace(0, 2 * np.pi, len(direction_labels), endpoint=False))
ax.set_xticklabels(direction_labels)

ax.set_title('Wind Rose - Wind Speed by Direction')
plt.show()

