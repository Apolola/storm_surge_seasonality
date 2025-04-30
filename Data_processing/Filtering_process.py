# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 14:08:23 2023

@author: aap207
"""

#Import all important Libraries

import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

# Load the data with xarray
# The asterisk symbol (*) represents the totatility of all available data where assigned
#obs_surge = xr.open_mfdataset ('C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Reanlysis_Totwater_1979-2010/reanalysis_waterlevel_dailymax_*_*_v1.nc')
#obs_surge

idir = 'C:/Users/aap207/OneDrive - Vrije Universiteit Amsterdam/Paper 1/Select_locations/Hourly_series/' 
ifile = os.path.join(idir, 'reanalysis_surge_hourly_*_*_v1.nc')

obs_surge = xr.open_mfdataset (ifile)
obs_surge = obs_surge.load()
obs_surge

cluster = 3925 #use 3925 for example

# Select the data for the specific station and drop NaNs
cleaned_station = obs_surge.surge.isel(stations=cluster).load().dropna(dim='time') # The butterworth low pass filter fails is quite sensitive to Nans value and fails if the timseries contains it

fs = 1/3600   # sample rate, Hz
cutoff = 0.0000000316880878140 #365day frequency  #0.0000003858024691358 30day frequency
nyq = 0.5 * fs  # Nyquist Frequency
order = 2       # sin wave can be approx represented as quadratic
#Calculate the normalized frequency
normal_cutoff = cutoff / nyq
# Get the filter coefficients  
b, a = butter(order, normal_cutoff, btype='low', analog=False)
y = filtfilt(b, a, cleaned_station)

# Calculate the difference between original and filtered
filtered_data = cleaned_station - y