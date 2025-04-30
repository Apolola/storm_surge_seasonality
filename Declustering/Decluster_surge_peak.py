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

# Step 3
#--------------------------------------Decluster the timeseries---------------------------------------------------          
indep = 36              # Number of hours to decluster storm events
quant_value = 0.80      # Percentile/quantile value
# Calculate the threshold
threshold = filtered_data.quantile(quant_value, dim='time', method='linear') # Method = linear doesn't do much, it is the default setting. options include nearest, midpoint, lower and higher
peaks = filtered_data.where(filtered_data > threshold, drop=True) # Drop True, drop all the series that are non-peaks

# Delustering process
selected_peaks = [] 
prev_peak = None  # Initialize the previous peak or the first peak as None 

for peak in peaks:
    window_start = peak.time - pd.Timedelta(hours=indep)
    window_end = peak.time + pd.Timedelta(hours=indep)

    if prev_peak is not None and prev_peak['window_end'] >= window_start:
        # Overlapping windows, compare peaks and select the one with the highest value
        if peak.values > prev_peak['peak'].values:
            prev_peak = {'window_start': window_start, 'window_end': window_end, 'peak': peak}
        else:
            continue
    else:
        # No overlap or first peak
        if prev_peak is not None:
            selected_peaks.append(prev_peak['peak'])  # Append the previous peak to the selected list

        # Update prev peak to the current peak
        prev_peak = {'window_start': window_start, 'window_end': window_end, 'peak': peak}

# Append the last declustered/selected peak
if prev_peak is not None:
    selected_peaks.append(prev_peak['peak'])
    
#--------------------------------------Top 117 peaks---------------------------------------------------    
# Convert selected_peaks to xarray DataArray
selected_peaks = xr.concat(selected_peaks, dim='time')
df = selected_peaks.to_dataframe()
sort_df = df.sort_values(by = 'surge', ascending= False)
Top_117 = sort_df[:117]
Top_117_Datetime_month = pd.to_datetime(Top_117.index)
Top_117_Datetime_month

Needed_data = Top_117.drop(columns=['station_x_coordinate','station_y_coordinate','stations','quantile'])
Needed_data = Needed_data.reset_index()
Needed_data['doy'] = Needed_data.time.dt.dayofyear
