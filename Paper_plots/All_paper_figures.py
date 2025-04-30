# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 13:20:31 2024

@author: aap207
"""

#%%%
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy.stats as sp        #used to perform statistical analysis
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patheffects as pe
import regionmask

obs_surge = xr.open_mfdataset('reanalysis_surge_hourly_*_*_v1.nc')

obs_surge['time'].values                               
Time = obs_surge['time']                       
latitude = obs_surge['station_y_coordinate']
longitude = obs_surge['station_x_coordinate']

#%%%#Load the aggregated primary season npz file
Primary = np.load (("final_primary_season_result.npz"), allow_pickle=True)
Primary
print (len(Primary))
print (Primary.files)

# Access arrays from the .npz file
Uniformitytest =Primary['uniformity_test']
print (len(Uniformitytest))
Season_number  = Primary['Optimal_season']
Season_number
primary_mean = Primary['primary_mean_directions']
primary_mean
primarymean_start = Primary['primary_season_start']
primarymean_start
primarymean_end = Primary['primary_season_end']
primarymean_end
start_end_length = Primary['primary_season_length']
start_end_length
primary_weight = Primary['primary_season_weight']
primary_weight
Monte_carlo_rsq = Primary['rsquared_value']
Monte_carlo_rsq
peak_dates_count = Primary['primary_event_count']
peak_dates_count
primary_surge_peak_mean= Primary['primary_meanlength_mag']
primary_surge_peak_mean
primary_surge_peak_cv = Primary['primary_meanlength_CV']
primary_surge_peak_cv
primary_surge_peak_sk = Primary['primary_meanlength_SK']
primary_surge_peak_sk
primary_surge_peak_kt = Primary['primary_meanlength_KT']
primary_surge_peak_kt
primary_stations_ids= Primary['ids']
primary_stations_ids

print ("The number of stations in the result is:", len(primary_stations_ids))

#There is a lower number of results than the available stations, so i filter what is not and what is available for plotting
all_station_ids = np.arange(43119)  #Total number of station point in the dataset

# Find the station IDs missing 
missing_station_ids = np.setdiff1d(all_station_ids, primary_stations_ids)  #setdiff1d finds the IDs in the array all_ids that are not in
print (missing_station_ids)
print (len(missing_station_ids))

lenght = []
for Length in start_end_length:
    if Length <= 60:
        lenght.append(Length)

print (len(lenght))
#%%%#Load the aggregated secondary season
Secondary = np.load ("final_secondary_season_result.npz")
Secondary
print (len(Secondary))
print (Secondary.files)

# Access arrays from the .npz file
secondary_mean = Secondary['secondary_mean_directions']
secondary_mean
secondary_mean_start = Secondary['secondary_season_start']
secondary_mean_start
secondary_mean_end = Secondary['secondary_season_end']
secondary_mean_end
Sec_start_end_length = Secondary['secondary_season_length']
Sec_start_end_length
secondary_weight = Secondary['secondary_season_weight']
secondary_weight
secondary_dates_count = Secondary['secondary_season_event_count']
secondary_dates_count
secondary_surge_peak_mean = Secondary['secondarymeanlength_mag']
secondary_surge_peak_mean
secondary_surge_peak_cv = Secondary['secondary_meanlength_CV']
secondary_surge_peak_cv
secondary_surge_peak_sk = Secondary['secondary_meanlength_sk']
secondary_surge_peak_sk
secondary_surge_peak_kt = Secondary['secondary_meanlength_kt']
secondary_surge_peak_kt
secondary_ids = Secondary['ids']
secondary_ids
print ("The number of stations in the result is:", len(secondary_surge_peak_mean))
#%%%#Filter the missing stations
missing_longitude = longitude[missing_station_ids]
missing_latitude = latitude[missing_station_ids]

# Select Europe to reduce the size of the ouput station plots for plotting
primary_processed_longitude = longitude[primary_stations_ids]
primary_processed_latitude = latitude[primary_stations_ids]

secondary_processed_longitude = longitude[secondary_ids]
secondary_processed_latitude = latitude[secondary_ids]

#select the coordinates of Europe
min_lat = 24   
max_lat = 73   
min_lon = -31.5  
max_lon = 60   

Europe_stations_primary = ((primary_processed_latitude >= min_lat) & (primary_processed_latitude <= max_lat) & 
                   (primary_processed_longitude >= min_lon) & (primary_processed_longitude <= max_lon))
Europe_primary = primary_stations_ids[Europe_stations_primary]
print (len(Europe_primary))

Europe_stations_secondary = ((secondary_processed_latitude >= min_lat) & (secondary_processed_latitude <= max_lat) & 
                   (secondary_processed_longitude >= min_lon) & (secondary_processed_longitude <= max_lon))
Europe_secondary = secondary_ids[Europe_stations_secondary]
print (len(Europe_secondary))

Europe_stations_missing = ((missing_latitude >= min_lat) & (missing_latitude <= max_lat) & 
                   (missing_longitude >= min_lon) & (missing_longitude <= max_lon))
Europe_missing = missing_station_ids[Europe_stations_missing]
print (len(Europe_missing))

Mask_Europe = ~np.isin(primary_stations_ids, Europe_primary)
Mask_Europe_uniformity = ~np.isin(missing_station_ids, Europe_missing)

Europe = np.isin(primary_stations_ids, Europe_primary)
Europe_uniformity = np.isin(missing_station_ids, Europe_missing)
#%%%'''#_____________________________________#_____ Number of surge seasons_______________#______________________________'''
fig = plt.figure(figsize=(20, 10), tight_layout= True)
ax = plt.axes(projection=ccrs.Robinson())
cmap1 = (mpl.colors.ListedColormap(['grey','skyblue', 'orange', 'red']))

sn = ax.scatter(primary_processed_longitude[Mask_Europe],primary_processed_latitude[Mask_Europe], s=6, alpha=1, c=Season_number[Mask_Europe],vmin=0, vmax=4, cmap=cmap1, transform=ccrs.PlateCarree())
sne = ax.scatter(primary_processed_longitude[Europe],primary_processed_latitude[Europe], s=0.2, alpha=0.75, c=Season_number[Europe],vmin=0, vmax=4, cmap=cmap1, transform=ccrs.PlateCarree())
sn1e = ax.scatter(missing_longitude[Europe_uniformity] , missing_latitude[Europe_uniformity], s=0.2, color='grey', alpha=0.85, transform=ccrs.PlateCarree())
sn1 = ax.scatter(missing_longitude[Mask_Europe_uniformity ] , missing_latitude[Mask_Europe_uniformity ], s= 6, color='grey', alpha=1, transform=ccrs.PlateCarree())
ax.coastlines(resolution='110m', color='black')
gl0 = ax.gridlines(draw_labels=True, linestyle='--', dms=True, x_inline=False, y_inline=False) #color='gray', linewidth=0.5
gl0.top_labels = False  # Remove top labels
gl0.right_labels = False  # Remove  ize for x-axis labels
gl0.xlabel_style = {'fontsize': 18}  # Set the fontsize for x-axis labels
gl0.ylabel_style = {'fontsize': 18}  # Set the fontsize for y-axis labels
ax.set_title("Number of surge seasons", fontweight='bold', pad=14, fontsize=30)
cbar = plt.colorbar(sn, ax=ax, orientation='vertical', shrink=0.9, aspect=20, pad=0.03)
cbar.set_ticks([0.5, 1.5, 2.5, 3.5]) # Set ticks at the center of each color segment
cbar.set_ticklabels(["0 -(16%)","1 - (56%)", "2 -(26%)", "3 -(2%)"])
cbar.ax.tick_params(labelsize=20)  # Adjust the font size here

plot_dir= 'Paper_plots/'
filename= 'season_number.pdf'
plt.savefig(plot_dir + filename, dpi=600)
plt.show()

#%%%
'''#_____________________________________#______only two seasons (considered)__________________________#______________________________'''
'''#From primary_staions_id which contain the results, find the number of stations with less tha 3 season'''
considered_seasons = np.where(Season_number < 3)[0]
print ('number of stations with less than 3 seasons:', len(considered_seasons))
considered_seasons_longitude = longitude[primary_stations_ids][considered_seasons]
considered_seasons_latitude = latitude[primary_stations_ids][considered_seasons]

considered_Monte_carlo_rsq = Monte_carlo_rsq[considered_seasons] 
considered_primary_mean = primary_mean[considered_seasons] 
considered_primarymean_start = primarymean_start[considered_seasons]
considered_primarymean_end = primarymean_end[considered_seasons]
considered_start_end_length = start_end_length[considered_seasons] 
considered_primary_weight = primary_weight[considered_seasons] *100
considered_peak_dates_count = peak_dates_count[considered_seasons] 
considered_primary_surge_peak_mean = primary_surge_peak_mean[considered_seasons] 
considered_primary_surge_peak_cv = primary_surge_peak_cv[considered_seasons] 
considered_primary_surge_peak_sk = primary_surge_peak_sk[considered_seasons] 
considered_primary_surge_peak_kt = primary_surge_peak_kt[considered_seasons] 

#Get indices where season number is 3 from the file of the secondary season and drop  missing,
array_for_3 = np.where(Season_number == 3)[0]
ids_to_remove = primary_stations_ids[array_for_3]
print('IDs to remove:', ids_to_remove)
mask = ~np.isin(secondary_ids, ids_to_remove)   # Create a mask to exclude specified indices
filtered_secondary_ids = secondary_ids[mask]
print(len(filtered_secondary_ids))

# filter longitude and latitude
secondary_filtered_long = longitude[secondary_ids][mask]
secondary_filtered_lat = latitude[secondary_ids][mask]

filtered_sec_start_end_length = Sec_start_end_length[mask]
filtered_secondary_dates_count = secondary_dates_count[mask]
filtered_secondary_weight = secondary_weight[mask]*100
filtered_secondary_mean = secondary_mean[mask]
filtered_secondary_surge_peak_mean = secondary_surge_peak_mean[mask]
filtered_secondary_surge_peak_cv = secondary_surge_peak_cv[mask]
filtered_secondary_surge_peak_sk = secondary_surge_peak_sk[mask]
filtered_secondary_surge_peak_kt = secondary_surge_peak_kt[mask]

#Filter again for the considered stations
# Select Europe to reduce the size of the station plots for plotting
min_lat = 24   
max_lat = 73   
min_lon = -31.5  
max_lon = 60   

Europe_considered_primary = ((considered_seasons_latitude >= min_lat) & (considered_seasons_latitude <= max_lat) & 
                   (considered_seasons_longitude >= min_lon) & (considered_seasons_longitude <= max_lon))
filtered_Europe_primary= considered_seasons[Europe_considered_primary]
print (len(filtered_Europe_primary))

Europe_considered_secondary = ((secondary_filtered_lat >= min_lat) & (secondary_filtered_lat <= max_lat) & 
                               (secondary_filtered_long >= min_lon) & (secondary_filtered_long <= max_lon))

filtered_Europe_secondary = filtered_secondary_ids[Europe_considered_secondary]
print (len(filtered_Europe_secondary))

Mask_Europe_primary = ~np.isin(considered_seasons,filtered_Europe_primary)
Mask_Europe_secondary = ~np.isin(filtered_secondary_ids,filtered_Europe_secondary)

Europe_primary = np.isin(considered_seasons , filtered_Europe_primary)
Europe_secondary = np.isin(filtered_secondary_ids,filtered_Europe_secondary)

#%%%'''#_____________________________________#_____ peak of the storm surge season _______________#______________________________'''
fig = plt.figure(figsize=(20, 24))
gs = fig.add_gridspec(2, 1, width_ratios=[1], height_ratios=[1, 1.2], wspace=0.5, hspace=0.1)
ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.Robinson())  
ax2 = fig.add_subplot(gs[1, 0], projection=ccrs.Robinson())    

# Plot 
cmap1 =mpl.colormaps['hsv_r']#.resampled(12)
pc_count = ax1.scatter(considered_seasons_longitude[Mask_Europe_primary], considered_seasons_latitude[Mask_Europe_primary], c=considered_primary_mean[Mask_Europe_primary],
                       vmin=0, vmax=360, s=5, cmap=cmap1, transform=ccrs.PlateCarree(), marker='o', alpha=1)
pc_count1 = ax1.scatter(considered_seasons_longitude[Europe_primary], considered_seasons_latitude[Europe_primary], c=considered_primary_mean[Europe_primary],
                      vmin=0, vmax=360, s=0.15, cmap=cmap1, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
ax1.coastlines(resolution='110m', color='black')
gl01=ax1.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl01.top_labels = False  # Remove top labels
gl01.right_labels = False  # Remove left labels
gl01.xlabel_style = {'fontsize': 19}  # Set the fontsize for x-axis labels
gl01.ylabel_style = {'fontsize': 19}  # Set the fontsize for y-axis labels
ax1.set_title(' Peak dates of the storm surge season \n season 1', fontsize=30, fontweight='bold', pad=14)
ax1.text(-0.04, 1.1, 'a', transform=ax1.transAxes, fontsize=23, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))

# Plot 
cmap2 =mpl.colormaps['hsv_r']#.resampled(12)
norm = mpl.colors.Normalize(vmin=0, vmax=360)
months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',  5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
pc_count = ax2.scatter(secondary_filtered_long[Mask_Europe_secondary], secondary_filtered_lat[Mask_Europe_secondary], c= filtered_secondary_mean[Mask_Europe_secondary],
                   vmin=0, vmax=360, s=5, cmap=cmap2, transform=ccrs.PlateCarree(), marker='o', alpha=1)
pc_count1 = ax2.scatter(secondary_filtered_long[Europe_secondary], secondary_filtered_lat[Europe_secondary], c=filtered_secondary_mean[Europe_secondary],
                      vmin=0, vmax=360, s=0.15, cmap=cmap2, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
ax2.coastlines(resolution='110m', color='black')
gl01=ax2.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl01.top_labels = False  # Remove top labels
gl01.right_labels = False  # Remove left labels
gl01.xlabel_style = {'fontsize': 19}  # Set the fontsize for x-axis labels
gl01.ylabel_style = {'fontsize': 19}  # Set the fontsize for y-axis labels
ax2.set_title('season 2', fontsize=30, fontweight='bold', pad=14)
ax2.text(-0.04, 1.1, 'b', transform=ax2.transAxes, fontsize=23, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))
# Create a single color bar for both plots
cbar = fig.colorbar( mpl.cm.ScalarMappable(norm=norm, cmap=cmap2), ax=ax2, orientation='horizontal',
    fraction=0.035, aspect=40, pad=0.09)
cbar.ax.tick_params(labelsize=22)
#cbar.set_label('Dates', fontsize=15,  labelpad=10)
cbar.set_ticks(np.arange(0, 361, 30))
cbar.set_ticklabels(["", "", "", "", "", "", "",
                    "", "", "", "", "", ""], color='black')
# Add month labels between circular plot angles
for month_num, tick_position in zip(range(1, 13), np.arange(15, 375, 30)):  # Start at 15 degrees and go up to 375 degrees
    month_name = months[month_num]
    cbar.ax.text(tick_position, -0.2, month_name, va='top', ha='center', color='black', fontsize = 22)

plot_dir= 'C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Select_locations/result_npz/Paper1_plots/'
filename= 'Season_1 direction.pdf'
plt.savefig(plot_dir + filename, dpi=600, format='pdf',bbox_inches='tight')
plt.show()

#%%%'''#_____________________________________#_____ Lenght of the storm surge season _______________#______________________________'''
# Create figure with gridspec
fig = plt.figure(figsize=(20, 24))
gs = fig.add_gridspec(2, 1, width_ratios=[1], height_ratios=[1, 1.2], wspace=0.5, hspace=0.1)
ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.Robinson())  
ax2 = fig.add_subplot(gs[1, 0], projection=ccrs.Robinson())    

# Create a colormap for markers
cmap1 =mpl.colormaps['plasma']
# Plot concentration period
pc_conc = ax1.scatter(considered_seasons_longitude[Mask_Europe_primary], considered_seasons_latitude[Mask_Europe_primary], c= considered_start_end_length[Mask_Europe_primary],
                     vmin=0, vmax=120, s=5, cmap=cmap1, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
pc_conc2 = ax1.scatter(considered_seasons_longitude[Europe_primary], considered_seasons_latitude[Europe_primary], c=considered_start_end_length[Europe_primary],
                      vmin=0, vmax=120, s=0.15, cmap=cmap1, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
ax1.coastlines(resolution='110m', color='black')
gl0 = ax1.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl0.top_labels = False  # Remove top labels
gl0.right_labels = False  # Remove right labels
gl0.xlabel_style = {'fontsize': 19}  # Set the fontsize for x-axis labels
gl0.ylabel_style = {'fontsize': 19}  # Set the fontsize for y-axis labels
ax1.set_title('Length of the storm surge season \n season 1', fontsize=30, fontweight='bold', pad=14)
ax1.text(-0.04, 1.1, 'a', transform=ax1.transAxes, fontsize=23, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))

# Create a colormap for markers
cmap2 =mpl.colormaps['plasma']
# Plot concentration period
sc_conc  = ax2.scatter(secondary_filtered_long[Mask_Europe_secondary], secondary_filtered_lat[Mask_Europe_secondary], c= filtered_sec_start_end_length [Mask_Europe_secondary],
                   vmin=0, vmax=120, s=5, cmap=cmap2, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
sc_conc2 = ax2.scatter(secondary_filtered_long[Europe_secondary], secondary_filtered_lat[Europe_secondary], c=filtered_sec_start_end_length [Europe_secondary],
                      vmin=0, vmax=120, s=0.15, cmap=cmap2, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
ax2.coastlines(resolution='110m', color='black')
gl0 = ax2.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl0.top_labels = False  # Remove top labels
gl0.right_labels = False  # Remove right labels
gl0.xlabel_style = {'fontsize': 19}  # Set the fontsize for x-axis labels
gl0.ylabel_style = {'fontsize': 19}  # Set the fontsize for y-axis labels
ax2.set_title('season 2', fontsize=30, fontweight='bold', pad=14)
ax2.text(-0.04, 1.1, 'b', transform=ax2.transAxes, fontsize=23, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))
cbar_sc_conc = plt.colorbar(sc_conc, ax=ax2, orientation='horizontal', fraction=0.040, aspect=40, pad=0.09, extend='max')
cbar_sc_conc.ax.tick_params(labelsize=22)  # Adjust the font size here
cbar_sc_conc.set_label('Duration (days)', fontsize=24, labelpad=10)
tick_positions = np.arange(0, 121, 20)
tick_labels = ['0', '20', '40', '60', '80', '100', '120']  
cbar_sc_conc.set_ticks(tick_positions)  # Set tick positions
cbar_sc_conc.set_ticklabels(tick_labels)  # Set tick labels

plot_dir= 'Paper1_plots/'
filename= 'Lenght of surge season.pdf'
plt.savefig(plot_dir + filename, dpi=600, format = 'pdf', bbox_inches='tight')
plt.show()

#%%%'''#_____________________________________#_____ Number of surge peaks and the average surge magnitude_______________#______________________________'''

primary_ids_filtered = primary_stations_ids[considered_seasons]
secondary_ids_filtered = filtered_secondary_ids

common_ids = np.intersect1d(primary_ids_filtered, secondary_ids_filtered)

primary_common_indices = np.where(np.isin(primary_ids_filtered, common_ids))[0]
secondary_common_indices = np.where(np.isin(secondary_ids_filtered, common_ids))[0]

primary_means_common = considered_primary_surge_peak_mean[primary_common_indices]
secondary_means_common = filtered_secondary_surge_peak_mean[secondary_common_indices]

# The ratio of season 1 to season 2
surge_mean_difference = ((secondary_means_common - primary_means_common)/ primary_means_common) * 100
max(secondary_means_common)
print (len(surge_mean_difference))
print('Difference in surge peak mean for common stations:', surge_mean_difference)

fig = plt.figure(figsize=(30, 20))
gs = fig.add_gridspec(2, 2, width_ratios=[1, 1], height_ratios=[1, 1], wspace=0.2, hspace=-0.2)

ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.Robinson())  
ax2 = fig.add_subplot(gs[0, 1], projection=ccrs.Robinson())  
ax3 = fig.add_subplot(gs[1, 0], projection=ccrs.Robinson())  
ax4 = fig.add_subplot(gs[1, 1], projection=ccrs.Robinson())   

# Plot the surge count
cmap1 =mpl.colormaps['Spectral_r']
pc_count = ax1.scatter(considered_seasons_longitude[Mask_Europe_primary], considered_seasons_latitude[Mask_Europe_primary], c=considered_peak_dates_count[Mask_Europe_primary]/39,
                       vmin=0, vmax=2.5, s=4, cmap=cmap1, transform=ccrs.PlateCarree(), marker='o', alpha=1)
pc_count = ax1.scatter(considered_seasons_longitude[Europe_primary], considered_seasons_latitude[Europe_primary], c=considered_peak_dates_count[Europe_primary]/39,
                      vmin=0, vmax=2.5, s=0.09, cmap=cmap1, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
ax1.coastlines(resolution='110m', color='black')
gl01=ax1.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl01.top_labels = False  # Remove top labels
gl01.right_labels = False  # Remove left labels
gl01.xlabel_style = {'fontsize': 17}  # Set the fontsize for x-axis labels
gl01.ylabel_style = {'fontsize': 17}  # Set the fontsize for y-axis labels
ax1.set_title('Average number of surge peaks \n season 1', fontsize=24, fontweight='bold', pad=12)
ax1.text(-0.04, 1.1, 'a', transform=ax1.transAxes, fontsize=20, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))

cmap2 =mpl.colormaps['Spectral_r']
# Plot the mean
pcc_conc_mean = ax2.scatter(considered_seasons_longitude[Mask_Europe_primary], considered_seasons_latitude[Mask_Europe_primary], c=considered_primary_surge_peak_mean[Mask_Europe_primary],
                     vmin=0, vmax=1.5, s=4, cmap=cmap2, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
pcc_conc2_mean = ax2.scatter(considered_seasons_longitude[Europe_primary], considered_seasons_latitude[Europe_primary], c=considered_primary_surge_peak_mean[Europe_primary],
                      vmin=0, vmax=1.5, s=0.09, cmap=cmap2, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
ax2.coastlines(resolution='110m', color='black')
gl0 = ax2.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl0.top_labels = False  # Remove top labels
gl0.right_labels = False  # Remove right labels
gl0.xlabel_style = {'fontsize': 17}  # Set the fontsize for x-axis labels
gl0.ylabel_style = {'fontsize': 17}  # Set the fontsize for y-axis labels
ax2.set_title('Mean surge peaks \n season 1', fontsize=24, fontweight='bold', pad=12)
ax2.text(-0.04, 1.1, 'b', transform=ax2.transAxes, fontsize=20, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))
cbar_pcc_conc_mean = plt.colorbar(pcc_conc_mean, ax=ax2, orientation='vertical', fraction=0.030, aspect=18, pad=0.02, extend='max')
cbar_pcc_conc_mean.ax.tick_params(labelsize=15)  # Adjust the font size here
cbar_pcc_conc_mean.set_label('Surge (m)', fontsize=16, labelpad = 10)
tick_positions = np.arange(0, 1.8, 0.3) 
tick_labels = ['0', '0.3', '0.6', '0.9', '1.2', '1.5']  
cbar_pcc_conc_mean.set_ticks(tick_positions)  # Set tick positions
cbar_pcc_conc_mean.set_ticklabels(tick_labels)  # Set tick labels

# Plot the surge count
cmap3 =mpl.colormaps['Spectral_r']#.resampled(5)
pc_count = ax3.scatter(secondary_filtered_long[Mask_Europe_secondary], secondary_filtered_lat[Mask_Europe_secondary], c= filtered_secondary_dates_count[Mask_Europe_secondary]/39,
                   vmin=0, vmax=2.5, s=4, cmap=cmap3, transform=ccrs.PlateCarree(), marker='o', alpha=1)
pc_count = ax3.scatter(secondary_filtered_long[Europe_secondary], secondary_filtered_lat[Europe_secondary], c=filtered_secondary_dates_count[Europe_secondary]/39,
                      vmin=0, vmax=2.5, s=0.09, cmap=cmap3, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
ax3.coastlines(resolution='110m', color='black')
gl01=ax3.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl01.top_labels = False  # Remove top labels
gl01.right_labels = False  # Remove left labels
gl01.xlabel_style = {'fontsize': 17}  # Set the fontsize for x-axis labels
gl01.ylabel_style = {'fontsize': 17}  # Set the fontsize for y-axis labels
ax3.set_title('season 2\n', fontsize=24, fontweight='bold', pad=12)
ax3.text(-0.04, 1.1, 'c', transform=ax3.transAxes, fontsize=20, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))
# Shared colorbar for A and C
cbar_shared_ac = plt.colorbar(pc_count, ax=[ax1, ax3], orientation='vertical', fraction=0.030, aspect=25, pad=0.04, extend='max')
cbar_shared_ac.ax.tick_params(labelsize=18)
cbar_shared_ac.set_label('Count', fontsize=18, labelpad=10)
cbar_shared_ac.set_ticks(np.arange(0, 2.6, 0.5))
cbar_shared_ac.set_ticklabels(['0', '0.5', '1.0', '1.5', '2.0', '2.5'])

# Plot the relative diferrence
cmap4 = mpl.colormaps['RdBu_r']
scc_conc_mean = ax4.scatter(secondary_filtered_long[Mask_Europe_secondary], secondary_filtered_lat[Mask_Europe_secondary], c=surge_mean_difference [Mask_Europe_secondary],
                     vmin=-20, vmax=20, s=5, cmap=cmap4, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
scc_conc_mean2 = ax4.scatter(secondary_filtered_long[Europe_secondary], secondary_filtered_lat[Europe_secondary], c=surge_mean_difference [Europe_secondary],
                      vmin=-20, vmax=20, s=0.2, cmap=cmap4, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
#scc_conc_mean = ax4.scatter(secondary_filtered_long[Mask_Europe_secondary], secondary_filtered_lat[Mask_Europe_secondary], c=filtered_secondary_surge_peak_mean[Mask_Europe_secondary],
 #                    vmin=0, vmax=2, s=4, cmap=cmap2, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)
#scc_conc_mean2 = ax4.scatter(secondary_filtered_long[Europe_secondary], secondary_filtered_lat[Europe_secondary], c=filtered_secondary_surge_peak_mean[Europe_secondary],
 #                     vmin=0, vmax=2, s=0.09, cmap=cmap2, transform=ccrs.PlateCarree(), marker='o', alpha=0.75)

ax4.coastlines(resolution='110m', color='black')
gl0 = ax4.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl0.top_labels = False  # Remove top labels
gl0.right_labels = False  # Remove right labelsss
gl0.xlabel_style = {'fontsize': 17}  # Set the fontsize for x-axis labels
gl0.ylabel_style = {'fontsize': 17}  # Set the fontsize for y-axis labels
ax4.set_title('Relative difference in the mean surge peaks:\n season 1 vs 2', fontsize=24, fontweight='bold', pad=12)
ax4.text(-0.04, 1.1, 'd', transform=ax4.transAxes, fontsize=20, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))
cbar_scc_conc_mean = plt.colorbar(scc_conc_mean, ax=ax4, orientation='vertical', fraction=0.030, aspect=18, pad=0.02, extend='both')
cbar_scc_conc_mean.ax.tick_params(labelsize=18)  # Adjust the font size here
cbar_scc_conc_mean.set_label('Relative difference (%)', fontsize=18, labelpad = 10)
plot_dir= 'C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Select_locations/result_npz/Paper1_plots/'
filename= 'Averag_number_and_magnitude.pdf'
plt.savefig(plot_dir + filename, dpi=600, format = 'pdf', bbox_inches='tight')
plt.show()
