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

# Step 6
###------- This line below runs the R script--------------------
# Pass Python list to R
robjects.globalenv['angles'] = robjects.FloatVector(angles)
# Execute the R script
robjects.r(r_script)        

#--------- Convert the result from R and save in python
# 1 Uniformity test- (0 represents uniform, 1 represents non-uniform)
uniformity_test_r = robjects.globalenv['uniformitytest']
# Convert the R list to a Python list
uniformity_test_py = list(uniformity_test_r)
uniformity_test_np = int (np.array(uniformity_test_py)[0])
print ("uniformity_test_np :", uniformity_test_np)

#----------------------------------------------------------------------------
# 2 Optimal number of season
Optimal_seasonN_r = robjects.globalenv['best_model_index']
Optimal_seasonN_py = list(Optimal_seasonN_r)
Optimal_seasonN_np = int(np.array(Optimal_seasonN_py)[0])
print ("Optimal_seasonN_np :", Optimal_seasonN_np)

#----------------------------------------------------------------------------
# 3 Sample mean
primary_mean_directions_r = robjects.globalenv['primary_mean']
primary_mean_directions_py = list(primary_mean_directions_r )
primary_mean_directions_py = (np.array(primary_mean_directions_py)[0])
print ("primary_mean_directions_py :", primary_mean_directions_py)

#----------------------------------------------------------------------------
# 4 surge start date
primary_season_start_r = robjects.globalenv['primary_mean_season_start']
primary_season_start_py = list(primary_season_start_r)
primary_season_start_py = (np.array(primary_season_start_py)[0])
print ("primary_season_start_py :", primary_season_start_py)

#----------------------------------------------------------------------------
# 5 Surge end date
primary_season_end_r = robjects.globalenv['primary_mean_season_end']
primary_season_end_py = list(primary_season_end_r)
primary_season_end_py = (np.array(primary_season_end_py)[0])
print ("primary_season_end_py :", primary_season_end_py)

#----------------------------------------------------------------------------
#6 Length of the season 
primary_season_length_r = robjects.globalenv['primary_angle_difference']
primary_season_length_py = list(primary_season_length_r)
primary_season_length_py = (np.array(primary_season_length_py)[0])
print ("primary_season_length_py :", primary_season_length_py)

#----------------------------------------------------------------------------
#7 mixing proportion
primary_weight_r = robjects.globalenv['primary_mix']
primary_weight_py = list(primary_weight_r)
primary_weight_py = (np.array(primary_weight_py)[0])
print ("primary_weight_py :", primary_weight_py)

#----------------------------------------------------------------------------
#8 Goodness of fit 
rsquared_value_r = robjects.globalenv['rsquared_value']
rsquared_value_py = list(rsquared_value_r)
rsquared_value_py = (np.array(rsquared_value_py)[0])
print ("rsquared_value_py :", rsquared_value_py)

#----------------------------------------------------------------------------
#9 event count
primary_count_r = robjects.globalenv['count_within_range1']
primary_count_py = list(primary_count_r)
primary_count_py = (np.array(primary_count_py)[0])

#----------------------------------------------------------------------------
if 'circ_correlation' in robjects.globalenv:
    circ_correlation_r = robjects.globalenv['circ_correlation']
    # Convert the R list to a Python list
    circ_correlation_py = list(circ_correlation_r)
    circ_correlation_py = (np.array(circ_correlation_py)[0])
    print ("circ_correlation:", circ_correlation_py)
else:
    print("No circular correlation")
#---------------------------------------------------------------------------
#10
primary_season_start = math.radians(primary_season_start_py)
primary_season_end = math.radians(primary_season_end_py)

store_radians = []
for event in angles:
    if primary_season_start <= primary_season_end:
        # Case 1: Range does not cross 360° (continuous)
        if primary_season_start <= event <= primary_season_end:
            store_radians.append(event)
    else:
        # Case 2: Range crosses 360°, select in two parts
        if event >= primary_season_start or event <= primary_season_end:
            store_radians.append(event)

# Convert the list of selected radians to a NumPy array
store_radians = np.array(store_radians)
store_radians

'''--------------------------------------'''
# Initialize dictionary to store surge values for each doy radian
surge_dict = {}
for rad in store_radians:
    # Filter the DataFrame for the current 'doy radian' value
    values =  Needed_data[ Needed_data['doy radian'] == rad]
    
    if not values.empty:
        surge_value = values['surge'].values
        surge_dict[rad] = surge_value
# Flatten the surge_dict into a list of tuples
flattened_surge = []
for rad, surges in surge_dict.items():
    for surge in surges:
        flattened_surge.append({'doy radian': rad, 'surge': surge})  

flattened_surge_df = pd.DataFrame(flattened_surge)
print("Flattened DataFrame:")
print(flattened_surge_df)

mean_flattened_surge_df =  flattened_surge_df.surge.mean()
mean_flattened_surge_df 
std_flattened_surge_df = flattened_surge_df.surge.std()
std_flattened_surge_df
cv_flattened_surge_df = (std_flattened_surge_df/mean_flattened_surge_df) * 100
cv_flattened_surge_df
skew_flattened_surge_df =  flattened_surge_df.surge.skew()
skew_flattened_surge_df
kurt_flattened_surge_df = flattened_surge_df.surge.kurtosis()
kurt_flattened_surge_df

#---------------secondary-------------------------------------------------------------
    # 11 mean direction
if 'secondary_mean' in robjects.globalenv:
    secondary_mean_directions_r = robjects.globalenv['secondary_mean']
    secondary_mean_directions_py = list(secondary_mean_directions_r )
    secondary_mean_directions_py = (np.array(secondary_mean_directions_r)[0])
    
    #----------------------------------------------------------------------------
    # 12 surge start date
    secondary_season_start_r = robjects.globalenv['secondary_mean_season_start']
    secondary_season_start_py = list(secondary_season_start_r)
    secondary_season_start_py = (np.array(secondary_season_start_py )[0])

    #----------------------------------------------------------------------------
    # 13 Surge end date
    secondary_season_end_r = robjects.globalenv['secondary_mean_season_end']
    secondary_season_end_py = list(secondary_season_end_r)
    secondary_season_end_py = (np.array(secondary_season_end_py )[0])
    
    #----------------------------------------------------------------------------
    #14 Length of the season 
    secondary_season_length_r = robjects.globalenv['secondary_angle_difference']
    secondary_season_length_py = list(secondary_season_length_r)
    secondary_season_length_py = (np.array(secondary_season_length_py)[0])
    
    #---------------------------------------------------------------------------
    #15
    secondary_season_start = math.radians(secondary_season_start_py)
    secondary_season_end = math.radians(secondary_season_end_py)
    store_secradians = []
    for secevents in angles:
        if secondary_season_start <= secondary_season_end:
        if secondary_season_start <= secevents <= secondary_season_end:
            store_secradians.append(secevents)  
        else: 
            if secevents >= secondary_season_start or secevents <= secondary_season_end:
            store_secradians.append(secevents)  
            
    store_secradians= np.array(store_secradians)
    store_secradians

    surge_dictsec = {}
    for rad in store_secradians:
        values =  Needed_data[Needed_data['doy radian'] == rad]
        
        if not values.empty:
            # Get the corresponding surge values and store them in the dictionary
            surge_value = values['surge'].values
            surge_dictsec[rad] = surge_value

    flattened_surgesec = []
    for rad, surges in surge_dictsec.items():
        for surge in surges:
            flattened_surgesec.append({'doy radian': rad, 'surge': surge})  
    
    flattened_surge_secdf = pd.DataFrame(flattened_surgesec)

    mean_flattened_surge_secdf =  flattened_surge_secdf.surge.mean()
    mean_flattened_surge_secdf
    std_flattened_surge_secdf = flattened_surge_secdf.surge.std()
    std_flattened_surge_secdf
    cv_flattened_surge_secdf = (std_flattened_surge_secdf/mean_flattened_surge_secdf) * 100
    cv_flattened_surge_secdf
    skew_flattened_surge_secdf =  flattened_surge_secdf.surge.skew()
    skew_flattened_surge_secdf
    kurt_flattened_surge_secdf = flattened_surge_secdf.surge.kurtosis()
    kurt_flattened_surge_secdf
                
    #----------------------------------------------------------------------------
    #15 mixing proportion
    secondary_Weight_r = robjects.globalenv['secondary_mix']
    secondary_Weight_py = list(secondary_Weight_r)
    secondary_weight_py = (np.array(secondary_Weight_py)[0])
    
    #----------------------------------------------------------------------------
    #16 mixing proportion
    secondary_count_r = robjects.globalenv['count_within_range2']
    secondary_count_py = list(secondary_count_r)
    secondary_count_py = (np.array(secondary_count_py)[0])
else:
    print("No Secondary season for this station")

#-----------------Tertiary----------------------------------------------------------
    # 16 mean direction
if 'Tertiary_mean' in robjects.globalenv:
    Tertiary_mean_directions_r = robjects.globalenv['Tertiary_mean']
    Tertiary_mean_directions_py = list(Tertiary_mean_directions_r )
    Tertiary_mean_directions_py = (np.array(Tertiary_mean_directions_py)[0])
    
    #----------------------------------------------------------------------------
    # 17 surge start date
    Tertiary_season_start_r = robjects.globalenv['Tertiary_mean_season_start']
    Tertiary_season_start_py = list(Tertiary_season_start_r)
    Tertiary_season_start_py = (np.array(Tertiary_season_start_py)[0])
    
    #----------------------------------------------------------------------------
    # 18 Surge end date
    Tertiary_season_end_r = robjects.globalenv['Tertiary_mean_season_end']
    Tertiary_season_end_py = list(Tertiary_season_end_r)
    Tertiary_season_end_py = (np.array(Tertiary_season_end_py)[0])
    
    #----------------------------------------------------------------------------
    # 19 Length of the season 
    Tertiary_season_length_r = robjects.globalenv['Tertiary_angle_difference']
    Tertiary_season_length_py = list(Tertiary_season_length_r)
    Tertiary_season_length_py = (np.array(Tertiary_season_length_py)[0])
    
    #----------------------------------------------------------------------------
    # 20 mixing proportion
    Tertiary_Weight_r = robjects.globalenv['Tertiary_mix']
    Tertiary_Weight_py = list(Tertiary_Weight_r)
    Tertiary_weight_py = (np.array(Tertiary_Weight_py)[0])
    
    #----------------------------------------------------------------------------
    # 21 mixing proportion
    Tertiary_count_r = robjects.globalenv['count_within_range3']
    # Convert the R list to a Python list
    Tertiary_count_py = list(Tertiary_count_r)
    Tertiary_count_py = (np.array(Tertiary_count_py)[0])
else:
    print("No Tertiary season for this station")

# Save the results for this station to a temporary file
temp_file = os.path.join(temp_dir1, f"results_{cluster}.npz")
np.savez(temp_file,
        uniformity_test = uniformity_test_np,
        Optimal_seasonN = Optimal_seasonN_np,
        primary_mean_directions = primary_mean_directions_py,
        primary_season_start = primary_season_start_py,
        primary_season_end = primary_season_end_py,
        primary_season_length = primary_season_length_py,
        primary_weight = primary_weight_py,
        rsquared_value = rsquared_value_py,
        primary_event_count = primary_count_py,
        primary_meanlength_mag = mean_flattened_surge_df,
        primary_meanlength_CV = cv_flattened_surge_df,
        primary_meanlength_sk= skew_flattened_surge_df,
        primary_meanlength_kt = kurt_flattened_surge_df,  
        Vonmises_rsquared = circ_correlation_py
        )   
        
temp_file2 = os.path.join(temp_dir2, f"results_{cluster}.npz")
np.savez(temp_file2,
        secondary_mean_directions = secondary_mean_directions_py,
        secondary_season_start = secondary_season_start_py,
        secondary_season_end = secondary_season_end_py,
        secondary_season_length = secondary_season_length_py,
        secondary_weight = secondary_weight_py,
        secondary_event_count = secondary_count_py,
        secondarymeanlength_mag = mean_flattened_surge_secdf,
        secondary_meanlength_CV = cv_flattened_surge_secdf,
        secondary_meanlength_sk= skew_flattened_surge_secdf,
        secondary_meanlength_kt = kurt_flattened_surge_secdf
        )  

temp_file3 = os.path.join(temp_dir3, f"results_{cluster}.npz")
np.savez(temp_file3,
        Tertiary_mean_directions = Tertiary_mean_directions_py,
        Tertiary_season_start = Tertiary_season_start_py,
        Tertiary_season_end = Tertiary_season_end_py,
        Tertiary_season_length = Tertiary_season_length_py,
        Tertiary_weight = Tertiary_weight_py,
        Tertiary_event_count = Tertiary_count_py,
        ) 