@author: Ayoola Apolola
"""
#Import all important Libraries
import os
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import scipy.stats as sp       
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap
from pandas.plotting import register_matplotlib_converters #used for converting between e.g. pandas timestamp/numpy datetime64/datetime.

# Load the data with xarray
# The asterisk symbol (*) represents the totatility of all available data where assigned
# Due to the size of the hourly surge data, it is more efficient to check this with the Daily max surge level data
idir = 'C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Select_locations/Hourly_series/' 
ifile = os.path.join(idir, 'reanalysis_surge_hourly_*_*_v1.nc')

obs_surge = xr.open_mfdataset (ifile)
obs_surge = obs_surge.load()
obs_surge
                            
time = obs_surge['time']                       
latitude = obs_surge['station_y_coordinate']
longitude = obs_surge['station_x_coordinate']

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#Resample to daily max
obs_surge = obs_surge.resample(time='1D').max()

# Show the total number of stations in the dataset
stations = obs_surge['stations'].values
print("Total number of stations in the dataset:", len(stations))

# Based on observations from surge levels across all stations, find the coastal location with surge levels above 9m
stations_to_drop = []
for station in stations:
    surge_level = obs_surge.sel(stations=station)
    if surge_level.max() >= 9:
        stations_to_drop.append(station)
        print (station)
        
count_dropped_stations = len(stations_to_drop)
print("Number of Dropped Stations:", count_dropped_stations)

for dropped_stations in stations_to_drop:
    print ("Dropped stations:", dropped_stations, "Latitude:", latitude.sel(stations=dropped_stations).values,
           "Longitude:", longitude.sel(stations=dropped_stations).values)
    
df = pd.DataFrame({'Dropped Stations': stations_to_drop,
                   'Latitude': latitude.sel(stations=stations_to_drop).values,
                   'Longitude': longitude.sel(stations=stations_to_drop).values})

#df.to_csv('dropped_station.csv', index=False, sep=';')

# Extract the dropped stations
dropped_stationss = obs_surge.sel(stations=stations_to_drop)

# Plot the stations
fig = plt.figure(figsize=(15.69, 8.27))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(resolution='110m', color='black')
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
# Not dropped stations with white markers
ax.scatter(longitude, latitude, 5, 'white', label='Remaining Stations')
# dropped stations with red markers
ax.scatter(dropped_stationss['station_x_coordinate'], dropped_stationss['station_y_coordinate'],
           5, 'red', label='Dropped Stations')
plt.title('Dropped stations = 5')

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
#Dropped_station = obs_surge.sel(stations=[7988, 13188, 13189, 13190, 13191, 13192, 13193])
file_path = '/Dropped_stations_daily'

for dropped_station in stations_to_drop:
    station_data = obs_surge.sel(stations=dropped_station)
    surge_data = station_data
    time_data = station_data['time']

    # Find maximum surge level and corresponding time
    max_surge = surge_data.max()
    max_surge_time = time_data[surge_data.argmax()]

    # Plot surge level
    plt.figure(figsize=(15.69, 8.27))
    surge_data.plot()
    plt.xlabel('Time')
    plt.ylabel('Waterlevel')
    plt.title(f'Waterlevel for Station {dropped_station}')
    
    # Annotation for maximum surge level and time
    plt.annotate(f'Max Surge Level: {max_surge:.2f}, Time: {max_surge_time.values}', 
                 xy=(max_surge_time, max_surge), xytext=(max_surge_time, max_surge + 0.2),
                 arrowprops=dict(arrowstyle='->'))
    
    # File path for saving the plot
    plot_filename = os.path.join(file_path, f'plot_{dropped_station}.png')
    plt.savefig(plot_filename)
    plt.close()
    
    # Print min and max water level values
    print(f'Minimum water level for Station {dropped_station}: {surge_data.min()}')
    print(f'Maximum water level for Station {dropped_station}: {surge_data.max()}')
