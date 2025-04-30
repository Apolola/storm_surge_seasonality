# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:54:25 2023

@author: aap207
"""

#Import all important Libraries
import os
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import scipy.stats as sp        #used to perform statistical analysis
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap
from pandas.plotting import register_matplotlib_converters #used for converting between e.g. pandas timestamp/numpy datetime64/datetime.

# Load the data with xarray
# The asterisk symbol (*) represents the totatility of all available data where assigned
idir = 'C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Reanlysis_Totwater_1979-2018/' 
ifile = os.path.join(idir, 'reanalysis_surge_dailymax_*_*_v1.nc')

obs_surge = xr.open_mfdataset (ifile)
obs_surge

# Load the data
obs_surge = obs_surge.load()
obs_surge

# Explore the data
obs_surge.info()
obs_surge.attrs
obs_surge.var
obs_surge.variables
obs_surge.data_vars

obs_surge['time'].values                               
time = obs_surge['time']                       
time

#Define the coordinates
latitude = obs_surge['station_y_coordinate']
latitude
longitude = obs_surge['station_x_coordinate']
longitude

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
# Show the total number of stations in the dataset
stations = obs_surge['stations'].values
print("Total number of stations in the dataset:", len(stations))

# Loop through the dataset and drop all stations with surge levels above 8.5m

obs_surge_1980 = obs_surge['surge'].sel(time = obs_surge['time'].dt.year >= 1980)

stations_to_drop = []
for station in stations:
    surge_level = obs_surge_1980.sel(stations=station)
    if surge_level.max() > 8.5:
        stations_to_drop.append(station)
        
count_dropped_stations = len(stations_to_drop)     #you cant use stations_to drop.Count() because stations to drop is a list function.it has to be this way 
print("Number of Dropped Stations:", count_dropped_stations)
        
# Drop rows with surge levels below 5m from the dataset
#obs_surge_filtered = obs_surge.sel(stations=~obs_surge['stations'].isin(stations_to_drop))#The tilde(~) symbol in this code inverts the original output..
                                                    #..rather than store the stations that should be dropped, it stores the stations that are not dropped.

# Display the stations and the coordinate of the stations not dropped
#for stationary in obs_surge_filtered['stations']:
#    print("Station:", stationary, "Latitude:", latitude.sel(stations=station).values, "Longitude:", longitude.sel(stations=station).values)


for dropped_stations in stations_to_drop:
    print ("Dropped stations:", dropped_stations, "Latitude:", latitude.sel(stations=dropped_stations).values,
           "Longitude:", longitude.sel(stations=dropped_stations).values)
    
df = pd.DataFrame({'Dropped Stations': stations_to_drop,
                   'Latitude': latitude.sel(stations=stations_to_drop).values,
                   'Longitude': longitude.sel(stations=stations_to_drop).values})

#df.to_csv('dropped_station.csv', index=False, sep=';')

# Extract the dropped stations
dropped_stationss = obs_surge_1980.sel(stations=stations_to_drop)

# Plot the remaining stations
fig = plt.figure(figsize=(15.69, 8.27))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(resolution='110m', color='black')
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

# Plot remaining stations with white markers
ax.scatter(longitude, latitude, 5, 'white', label='Remaining Stations')

# Plot dropped stations with red markers
ax.scatter(dropped_stationss['station_x_coordinate'], dropped_stationss['station_y_coordinate'],
           5, 'red', label='Dropped Stations')

plt.title('Dropped stations = 5')

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
# Loop through dropped stations

file_path = 'C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Dropped_stations_daily_1980'

for dropped_station in stations_to_drop:
    station_data = obs_surge_1980.sel(stations=dropped_station)
    surge_data = station_data
    time_data = station_data['time']

    # Find maximum surge level and corresponding time
    max_surge = surge_data.max()
    max_surge_time = time_data[surge_data.argmax()]

    # Plot water level data
    plt.figure(figsize=(15.69, 8.27))
    surge_data.plot()
    plt.xlabel('Time')
    plt.ylabel('Waterlevel')
    plt.title(f'Waterlevel for Station {dropped_station}')
    
    # Add annotation for maximum surge level and time
    plt.annotate(f'Max Surge Level: {max_surge:.2f}, Time: {max_surge_time.values}', 
                 xy=(max_surge_time, max_surge), xytext=(max_surge_time, max_surge + 0.2),
                 arrowprops=dict(arrowstyle='->'))
    
    # Define the file path for saving the plot
    plot_filename = os.path.join(file_path, f'plot_{dropped_station}.png')

    # Save the plot to the specified file path
    plt.savefig(plot_filename)

    # Close the plot to release resources (optional)
    plt.close()
    
    # Print min and max water level values
    print(f'Minimum water level for Station {dropped_station}: {surge_data.min()}')
    print(f'Maximum water level for Station {dropped_station}: {surge_data.max()}')

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
# Resample the filtered dataset from daily to annual
Dropped_stations_annual_max_surge = obs_surge_1980.sel(stations=stations_to_drop).resample(time='AS').max(dim='time')

# Loop through the dropped stations and plot their annual time series
file_path = 'C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Dropped_stations_Annual_1980'

for dropped_station in stations_to_drop:
    station_data = Dropped_stations_annual_max_surge.sel(stations=dropped_station)
    surge_data = station_data

    # Create a figure and axis
    plt.figure(figsize=(15.69, 8.27))
    surge_data.plot()
    plt.xlabel('Year')
    plt.ylabel('Surge Levels')
    plt.title(f'Annual Time Series for Dropped Station {dropped_station}')
    
    # Define the file path for saving the plot
    plot_filename = os.path.join(file_path, f'plot_{dropped_station}.png')

    # Save the plot to the specified file path
    plt.savefig(plot_filename)

    # Close the plot to release resources (optional)
    plt.close()


#---------------------------------------------------------------------------------------------------------------------
#---------------Plot the mean and standard deviation of the global max per selected station-----------------------------------------------

file_path = 'C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Dropped_stations_Anuall(mnstd)_1980'
for dropped_station in stations_to_drop:
    station_data = Dropped_stations_annual_max_surge.sel(stations=dropped_station)
    surge_data = station_data
    surge_mean = surge_data.mean(dim='time')
    surge_std = surge_data.std(dim='time')
    
    # Plot the station max annual value
    fig, ax = plt.subplots(figsize=(15.69, 8.27))
    ax.plot(surge_data.indexes['time'], surge_data, label='Original')
    
    # Plot the mean and standard deviation lines
    ax.axhline(y=surge_mean, color='red', linestyle='--', label='Station Mean')
    ax.axhline(y=surge_std, color='blue', linestyle='--', label='Standard Deviation')
    
    # Add a legend, title, and show the plot
    ax.legend(loc='best')
    ax.set_title(f'Annual Surge maxima for Station {dropped_station}')
    plt.xlabel('Year')
    plt.ylabel('Surge Levels (m)')
    
    # Close the plot to release resources (optional)
    plt.close()
    
    # Define the file path for saving the plot
    plot_filename = os.path.join(file_path, f'plot_{dropped_station}.png')

    # Save the plot to the specified file path
    plt.savefig(plot_filename)

    # Close the plot to release resources (optional)
    plt.close()

#####################################################################################################################

for dropped_station in stations_to_drop:
    droppeds_station = Dropped_stations_annual_max_surge.sel(stations=[13191])  # Replace with the actual station name
    surge_data = droppeds_station  # Get the numpy array from the xarray DataArray
    
ranked_surge_data = surge_data.rank(dim='time')
emp_exc_prob = ranked_surge_data/(ranked_surge_data.size+1)                  # empirical exceedance probabilities of the annual maxima
emp_cum_prob = emp_exc_prob                                              # empirical cumalative probabilities of the annual maxima (= inverse of exceedance probability)
emp_rp = 1/emp_exc_prob                                                      # return periods of the annual maxima
    
# Flatten the array, sort it in descending order, and then reshape it back to the original shape
#sorted_surge_data = np.sort(emp_rp.flatten())[::-1].reshape(surge_data.shape)
#sorted_surge_data_xr = xr.DataArray(sorted_surge_data, coords=droppeds_station.coords, dims=droppeds_station.dims)
    
#Step 2
cum_prob_x = np.arange(0.01,1,0.001)               # create 2d numpy array with probability range 0.01-1, with steps of 0.001
exc_prob_x = 1 - cum_prob_x                        # exceedance probabilities
rp_x = 1/(exc_prob_x)                              # return periods

#Step 3
gumbel_variate = -np.log(-np.log(cum_prob_x))      # take the double log, also see 'https://en.wikipedia.org/wiki/Gumbel_distribution#Computational_methods'

#Step 4
return_periods = np.array([2,5,10,25,50,100,250,500,1000])

[location,scale] = sp.gumbel_r.fit(surge_data)  # fit the gumbel_r distribution to our data to obtain estimates of the location and scale parameter

#Figure 1: Gumbel distribution and data plotted with normal x and y axes
plt.figure()
plt.plot(emp_rp,surge_data,'bo')
plt.plot(rp_x,sp.gumbel_r.ppf(cum_prob_x,location,scale))
plt.xlabel('Return Period (yrs)')
plt.ylabel('Value [m]')

#Figure 2: Same as Figure 1, but now the x-axis scale is logarithmic
plt.figure()
plt.semilogx(emp_rp,surge_data,'bo')
plt.semilogx(rp_x,sp.gumbel_r.ppf(cum_prob_x,location,scale))
plt.xlabel('Return Period (yrs)')
plt.ylabel('Value [m]')
    
#Figure 3: Gumbel variate on the x-axis -> double log scale used for plotting
plt.figure()
plt.plot(-np.log(-np.log(emp_cum_prob)),surge_data, 'ob')
plt.plot(gumbel_variate,sp.gumbel_r.ppf(cum_prob_x,location,scale))
plt.xlabel('Gumbel variate = -ln(-ln($P_{cum}$))')
plt.ylabel('Value [m]')

        
#Figure 4: Same as Figure 3, but now the x-axis shows the return period instead of the Gumbel variate
plt.figure()
plt.plot(-np.log(-np.log(emp_cum_prob)),surge_data, 'ob')
plt.plot(gumbel_variate,sp.gumbel_r.ppf(cum_prob_x,location,scale))
labels = [str(i) for i in return_periods]
plt.xticks(ticks = -np.log(-np.log(1 - 1/return_periods)), labels = labels)
plt.grid()
plt.xlabel('Return Period (yrs)')
plt.ylabel('Value [m]');   
    
    
return_periods = np.array([2,5,10,25,50,100,250,500,1000])
probs = 1./return_periods                                               # exceedance probabilities
rps_out = [return_periods,sp.gumbel_r.ppf(1-probs,location,scale)]      # Percent Point Function (PPF); inverse of CDF-percentiles (CDF = cumulative distribution function)
df = pd.DataFrame({'return periods (yrs)': rps_out[0],'surge level (m)': rps_out[1]}) # make a dataframe of it: easier to look at the data
df

# prepare bootstrapping
nr = 599 # number of bootstrap repetitions Wilcox, R. R. (2010). Fundamentals of modern statistical methods: Substantially improving power and accuracy. Springer.
ns = surge_data.shape[0]              # number of annual maxima
loc,sca = sp.gumbel_r.fit(surge_data) # location and scale parameter when gumbel is fitted to annual maxima (1980-2009)
location = np.zeros((nr,))               # array with zeros
scale = np.zeros_like(location)           # array with zeros
peaks = surge_data.values                   # annual maxima
    
# perform bootstrapping
for rpi in range(nr):                                     # bootstrap for-loop (599 repetitions)
    boot = np.random.choice(peaks.flatten(), size=(ns,), replace=True) # randomly select 30 samples from the 30 annual maxima, with replacement
    location[rpi],scale[rpi] = sp.gumbel_r.fit(boot)      # fit the gumbel distribution to obtain location and scale estimates
        
        
# extract 5th and 95th percentile parameter estimates
bootparamsci = {'location':location,'scale':scale}        # combine the location and scale parameter arrays in a python dictionary
    
location5 = np.percentile(bootparamsci['location'],5)     # 5th percentile location parameter
location95 = np.percentile(bootparamsci['location'],95)   # 95th percentile location parameter
scale5 = np.percentile(bootparamsci['scale'],5)           # 5th percentile scale parameter
scale95 = np.percentile(bootparamsci['scale'],95)         # 95th percentile scale parameter
    
    
# plot Figure 4 again, now with the 90% confidence interval
plt.figure()
plt.plot(-np.log(-np.log(emp_cum_prob)),surge_data, 'ob',label='empirical distribution (Weibull)')
plt.plot(gumbel_variate,sp.gumbel_r.ppf(cum_prob_x,loc,sca),label='gumbel distribution')
# fill_between takes three arguments: x; y1 (5th percentile, lower bound); y2 (95th percentile, upper bound)
# alpha makes the color transparent
plt.fill_between(gumbel_variate,sp.gumbel_r.ppf(cum_prob_x,location5,scale5),sp.gumbel_r.ppf(cum_prob_x,location95,scale95),alpha=0.4,label='90% confidence interval')
labels = [str(i) for i in return_periods]
plt.legend(loc='upper left')
plt.xticks(ticks = -np.log(-np.log(1 - 1/return_periods)), labels = labels)
plt.grid()
plt.xlabel('Return Period (yrs)')
plt.ylabel('Value [m]');













