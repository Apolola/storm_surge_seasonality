# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 13:26:47 2024

@author: aap207
"""
import os
import xarray as xr
import pandas as pd
import numpy as np
import geopandas as gpd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from cartopy.mpl.geoaxes import GeoAxes
from mpl_toolkits.axes_grid1 import AxesGrid
import cartopy as crt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.patheffects as pe
from matplotlib.ticker import FormatStrFormatter
import regionmask

obs_surge = xr.open_mfdataset('reanalysis_surge_hourly_*_*_v1.nc')
obs_surge
                          
Time = obs_surge['time']                       
Time

latitude = obs_surge['station_y_coordinate']
longitude = obs_surge['station_x_coordinate']

#bathymetry 
Bed_level_data = xr.open_mfdataset('/IPCC_reference_regions/bedlevel.nc')
Bed_level_data.load()

pxyn = Bed_level_data.to_dataframe()
pxyn.keys()

#IPCC ref region
Ipcc_reference_regions = gpd.read_file('/IPCC_reference_regions/IPCC-WGI-reference-regions-v4.shp')
Ipcc_reference_regions.keys()
Ipcc_reference_regions[['Continent', 'Type', 'Name']]
#%%%
Primary = np.load (("/final_primary_season_surge_result.npz"), allow_pickle=True)
Primary
print (len(Primary))
print (Primary.files)

All_primary_season_events = Primary['primary_season_events']
surge_column = []
for event in All_primary_season_events:
    surge_column.append(event[:, 1])

surge_column = np.array(surge_column, dtype='object') #print(len(surge_column)) #print(np.shape(surge_column))
df__testp = pd.DataFrame(surge_column)
df_try = df__testp[0]
df_try[0]

primary_season_events = surge_column
season = Primary['optimal_season']
primary_stations_idss = Primary['ids']

print ("The number of stations in the result is:", len(primary_stations_idss))
all_station_ids = np.arange(43119)  

# Find the station IDs missing in array7
missing_station_ids = np.setdiff1d(all_station_ids, primary_stations_idss)  
print (missing_station_ids)
print (len(missing_station_ids))

#%%%#Filter the missing stations

considered_seasons = np.where(season < 3)[0]
print ('number of stations with less than 3 seasons:', len(considered_seasons))
filtered_longitude  = longitude[primary_stations_idss][considered_seasons].load()
filtered_latitude = latitude[primary_stations_idss][considered_seasons].load()

primary_season_events = primary_season_events[considered_seasons]
primary_stations_ids = primary_stations_idss[considered_seasons]

change_pxyn_index = pxyn['bedlevel'].reset_index(drop = True)
bedlevel = change_pxyn_index

Surge_filtered = pd.DataFrame({'Longitude':filtered_longitude.values, 'Latitude':filtered_latitude.values,'Surge_data':primary_season_events,}, primary_stations_ids.copy())

df_filtered_coordinate = pd.DataFrame({'Longitude':filtered_longitude.values, 'Latitude':filtered_latitude.values}, primary_stations_ids.copy())
df_filtered_coordinate = pd.merge(df_filtered_coordinate, bedlevel, left_index=True, right_index=True)
gdf_coor = gpd.GeoDataFrame(df_filtered_coordinate, geometry=gpd.points_from_xy(df_filtered_coordinate.Longitude, df_filtered_coordinate.Latitude))    
gdf_coor = gdf_coor.set_crs('epsg:4326')
gdf_regions_join = gpd.sjoin(gdf_coor, Ipcc_reference_regions, how="left")
gdf_regions_join = gdf_regions_join.groupby(gdf_regions_join.index).first()
df_regions = pd.DataFrame(gdf_regions_join)
df_regions.keys()

# Some filtering of locations and resetting of labels
df = df_regions.loc[(df_regions.Continent != 'POLAR') & (df_regions.Type != 'Ocean') & (df_regions.bedlevel>-125)]
df = df.sort_values(by=['index_right'])
df.keys()
regions = df['Name'].unique()
abrev = df['Acronym'].unique()
count = df.groupby('Name').transform('count')['Latitude']
count_df = count.reset_index()
count_df = count_df.set_index('index') 
count_df = count_df.rename(columns={'Latitude':'count'})
df = pd.merge(df, count_df, left_index=True, right_index=True)
acronym_counts = df.groupby('Name')['Acronym'].value_counts().unstack(fill_value=0) #count the number of output stations
acronym_counts.max()

# Drop rows where 'column_name' is less than 100
df = df[df['count'] > 99]
df['Name'].unique()
regions = df['Name'].unique()
acronym_counts_again = df.groupby('Name')['Acronym'].value_counts().unstack(fill_value=0)
acronym_counts_again.max()

df['ivalue'] = 0
for i in range(0,len(regions)):
    df.loc[df['Name'] == regions[i], 'ivalue'] = i
regions = df['Name'].unique()
abrev = df['Acronym'].unique()
print(abrev)

# plot on global map
plot = True
if plot == True:
    crg = crt.crs.PlateCarree() # the one we have defined the data
    crgp = crt.crs.Robinson() # the one to plot the data
    from matplotlib.colors import ListedColormap
    clim=[0,len(regions)] 
    cm = ListedColormap(sns.color_palette('nipy_spectral', len(regions)).as_hex()) 
      
    fig = plt.figure(figsize=(20,10)) 
    ax = fig.add_subplot(111, projection=crt.crs.Robinson()) 
    ax.set_global()
    ax.set_extent([-180, 180, -90, 90], crg)   
    # Identify european coastal points
    lonmin = -35; lonmax = 50;latmin = 20;latmax = 80;depththresh = -20
    ioceaneu = df_regions[(df_regions['bedlevel']<depththresh) &(df_regions['Latitude']<=latmax)&(df_regions['Latitude']>=latmin)&(df_regions['Longitude']>=lonmin)&(df_regions['Longitude']<=lonmax)].index
    ioceanNeu = df_regions[(df_regions['bedlevel']<depththresh) &((df_regions['Latitude']>latmax)|(df_regions['Latitude']<latmin)|(df_regions['Longitude']<lonmin)|(df_regions['Longitude']>lonmax))].index
    # Identify coastal points    
    icoast =df_regions[df_regions['bedlevel']>=depththresh].index
    alfaoceaneu = 0.1; alfaoceanNeu = 0.4; alfacoast = 1; psoceaneu = 4; psoceanNeu = 20; pscoast = 8
    # scatter plot
    bs=ax.scatter(x=df_regions.loc[ioceaneu,'Longitude'].values,y=df_regions.loc[ioceaneu,'Latitude'].values,alpha=alfaoceaneu,s=psoceaneu,color='azure',transform=crg)
    bs=ax.scatter(x=df_regions.loc[ioceanNeu,'Longitude'].values,y=df_regions.loc[ioceanNeu,'Latitude'].values,alpha=alfaoceanNeu,s=psoceanNeu,color='azure',transform=crg)
    bs=ax.scatter(x=df_regions.loc[icoast,'Longitude'].values,y=df_regions.loc[icoast,'Latitude'].values,alpha=alfacoast,s=pscoast,color='azure',transform=crg)
    bs=ax.scatter(x=df.loc[:,'Longitude'].values,y=df.loc[:,'Latitude'].values,alpha=alfacoast,s=pscoast,c=df.loc[:,'ivalue'].values,cmap=cm,transform=crg,zorder=1)
    # add background       
    ax.add_feature(crt.feature.LAND.with_scale('10m'),facecolor='gray',zorder=4,alpha=0.20)
    ax.add_feature(crt.feature.LAKES.with_scale('10m'), facecolor='gray',zorder=5,alpha=0.05)        
    ax.add_feature(crt.feature.OCEAN.with_scale('10m'), edgecolor='face', facecolor='white')
    # Format lat lon grid    
    gl = ax.gridlines(crs=crg, draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.yline = gl.xlines = True
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.ylabel_style = {'size': 12, 'color': 'gray'}
    gl.xlabel_style = {'rotation': 0, 'size': 12, 'color': 'gray'}
    gl.top_labels = gl.right_labels = False
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90.,91.,30))
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(-180.,181.,40))
    # plot names
    text_kws = dict(bbox=dict(color="none", zorder=101),color="k", fontsize=10,path_effects=[pe.withStroke(linewidth=2.5, foreground="w")],)
    regionmask.defined_regions.ar6.land.plot(ax=ax,text_kws=text_kws, add_ocean=False,label="abbrev")

    # colorbar
    ax.set_title("Reference regions with a primary surge season", fontweight='bold', pad=14, fontsize=20)
    ax.text(-0.04, 1.05, 'a', transform=ax.transAxes, fontsize=20, verticalalignment='top', horizontalalignment='left',
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.2'))
    cbar= plt.colorbar(bs,ax=ax,orientation='vertical',shrink=0.9,pad=0.05)
    cbar.set_ticks(np.arange(clim[0],clim[1]))
    cbar.set_ticklabels(regions)  
    cbar.ax.tick_params(labelsize=10)
ax.grid(True)
plot_dir= '/Paper_plots/'
filename= 'IPCC_primary_region.pdf'
plt.savefig(plot_dir + filename, dpi=600, format='pdf', bbox_inches='tight')
plt.show()

df_stats = pd.merge(df, Surge_filtered['Surge_data'], left_index=True, right_index=True)
df_stats = df_stats.drop(columns={'Continent','geometry','Longitude', 'Latitude', 'bedlevel','index_right','Type'})#.sort_values(by='Name')
df_stats.keys()
Acronym = df_stats['Acronym'].unique()
sort_regions = df_stats['Name'].unique()

df_melt_rel_bias = pd.melt(df_stats[['Name','Surge_data','ivalue']],id_vars=['Name','ivalue'])
df_melt_rel_bias['index'] = df_stats.index.copy()
df_melt_rel_bias = df_melt_rel_bias.set_index('index') 
df_melt_rel_bias = df_melt_rel_bias.drop(columns='variable').dropna()
df_melt_rel_bias.keys()

df_melt_rel_bias_exploded = df_melt_rel_bias.explode('value')
#%%%
secondary = np.load (("final_secondary_season_surge_result.npz"), allow_pickle=True)
secondary 
print (len(secondary ))
print (secondary.files)

All_secondary_season_events = secondary ['secondary_season_events']
secondary_surge_column = []
for event in All_secondary_season_events:
    secondary_surge_column.append(event[:, 1])

secondary_surge_column = np.array(secondary_surge_column, dtype='object') 
df__tests = pd.DataFrame(secondary_surge_column)

secondary_season_events = secondary_surge_column
secondary_stations_ids = secondary['ids']

print ("The number of stations in the result is:", len(secondary_stations_ids))
all_station_ids = np.arange(43119)  

# Find the station IDs missing in array7
missing_station_ids = np.setdiff1d(all_station_ids,secondary_stations_ids)  
print (missing_station_ids)
print (len(missing_station_ids))
#%%%#Filter the missing stations

array_for_3 = np.where(season == 3)[0]
ids_to_remove = primary_stations_idss[array_for_3]
print('IDs to remove:', ids_to_remove)
mask = ~np.isin(secondary_stations_ids, ids_to_remove)   # Create a mask to exclude specified indices
filtered_secondary_ids = secondary_stations_ids[mask]
print(len(filtered_secondary_ids))

# filter longitude and latitude... with the mask
filtered_longitudeS = longitude[secondary_stations_ids][mask].load()
filtered_latitudeS  = latitude[secondary_stations_ids][mask].load()

secondary_season_events = secondary_season_events[mask]
secondary_stations_ids = secondary_stations_ids[mask]

change_pxyn_index = pxyn['bedlevel'].reset_index(drop = True)
bedlevel = change_pxyn_index

Surge_filteredS = pd.DataFrame({'Longitude':filtered_longitudeS.values, 'Latitude':filtered_latitudeS.values,'Surge_data':secondary_season_events,}, secondary_stations_ids.copy())
df_filtered_coordinateS = pd.DataFrame({'Longitude':filtered_longitudeS.values, 'Latitude':filtered_latitudeS.values}, secondary_stations_ids.copy())
df_filtered_coordinateS = pd.merge(df_filtered_coordinateS, bedlevel, left_index=True, right_index=True)
gdf_coorS = gpd.GeoDataFrame(df_filtered_coordinateS, geometry=gpd.points_from_xy(df_filtered_coordinateS.Longitude, df_filtered_coordinateS.Latitude))    
gdf_coorS = gdf_coorS.set_crs('epsg:4326')
gdf_regions_joinS = gpd.sjoin(gdf_coorS, Ipcc_reference_regions, how="left")
gdf_regions_joinS = gdf_regions_joinS.groupby(gdf_regions_joinS.index).first()
df_regionS = pd.DataFrame(gdf_regions_joinS)
df_regionS.keys()
df_regionS['Name'].unique()

# Some filtering of locations and resetting of labels
dfS = df_regionS.loc[(df_regionS.Continent != 'POLAR') & (df_regionS.Type != 'Ocean') & (df_regionS.bedlevel>-125)]
dfS = dfS.sort_values(by=['index_right'])
dfS.keys()
dfS['Acronym'].unique()
regionS = dfS['Name'].unique()
abrevS = dfS['Acronym'].unique()
countS = dfS.groupby('Name').transform('count')['Latitude']
count_dfS = countS.reset_index()
count_dfS = count_dfS.set_index('index') 
count_dfS = count_dfS.rename(columns={'Latitude':'count'})
dfS = pd.merge(dfS, count_dfS, left_index=True, right_index=True)
df_allS = dfS
Second_acronym_counts = df_allS.groupby('Name')['Acronym'].value_counts().unstack(fill_value=0)
Second_acronym_counts.max()
# Drop rows where 'column_name' is less than 100
dfS = dfS[dfS['count'] >= 100]
dfS  = dfS[(dfS['Acronym'] != 'NEU') & (dfS['Acronym'] != 'WCE')]   # NEU and WCE were dropped because the output station with two season was less than 20% of that with one season 
#dfS = dfS[~dfS['Acronym'].isin(['NEU', 'WEF'])]  Alternative way to do the step above
regionS = dfS['Name'].unique()

dfS['ivalue'] = 0
for i in range(0,len(regionS)):
    dfS.loc[dfS['Name'] == regionS[i], 'ivalue'] = i
regionS = dfS['Name'].unique()
abrevS = dfS['Acronym'].unique()

# plot on global map
plot = True
if plot == True:
    crg = crt.crs.PlateCarree() # the one we have defined the data
    crgp = crt.crs.Robinson() # the one to plot the data
    from matplotlib.colors import ListedColormap
    clim=[0,len(regionS)] 
    cm = ListedColormap(sns.color_palette('nipy_spectral', len(regionS)).as_hex()) 
      
    fig = plt.figure(figsize=(20,10)) 
    ax = fig.add_subplot(111, projection=crt.crs.Robinson()) 
    ax.set_global()
    ax.set_extent([-180, 180, -90, 90], crg)   
    # Identify european coastal points
    lonmin = -35; lonmax = 50;latmin = 20;latmax = 80;depththresh = -20
    ioceaneu = df_regionS[(df_regionS['bedlevel']<depththresh) &(df_regionS['Latitude']<=latmax)&(df_regionS['Latitude']>=latmin)&(df_regionS['Longitude']>=lonmin)&(df_regionS['Longitude']<=lonmax)].index
    ioceanNeu = df_regionS[(df_regionS['bedlevel']<depththresh) &((df_regionS['Latitude']>latmax)|(df_regionS['Latitude']<latmin)|(df_regionS['Longitude']<lonmin)|(df_regionS['Longitude']>lonmax))].index
    # Identify coastal points    
    icoast =df_regionS[df_regionS['bedlevel']>=depththresh].index
    alfaoceaneu = 0.1; alfaoceanNeu = 0.4; alfacoast = 1; psoceaneu = 4; psoceanNeu = 20; pscoast = 8
    # scatter plot
    bs=ax.scatter(x=df_regionS.loc[ioceaneu,'Longitude'].values,y=df_regionS.loc[ioceaneu,'Latitude'].values,alpha=alfaoceaneu,s=psoceaneu,color='azure',transform=crg)
    bs=ax.scatter(x=df_regionS.loc[ioceanNeu,'Longitude'].values,y=df_regionS.loc[ioceanNeu,'Latitude'].values,alpha=alfaoceanNeu,s=psoceanNeu,color='azure',transform=crg)
    bs=ax.scatter(x=df_regionS.loc[icoast,'Longitude'].values,y=df_regionS.loc[icoast,'Latitude'].values,alpha=alfacoast,s=pscoast,color='azure',transform=crg)
    bs=ax.scatter(x=dfS.loc[:,'Longitude'].values,y=dfS.loc[:,'Latitude'].values,alpha=alfacoast,s=pscoast,c=dfS.loc[:,'ivalue'].values,cmap=cm,transform=crg,zorder=1)
    # add background       
    ax.add_feature(crt.feature.LAND.with_scale('10m'),facecolor='gray',zorder=4,alpha=0.20)
    ax.add_feature(crt.feature.LAKES.with_scale('10m'), facecolor='gray',zorder=5,alpha=0.05)        
    ax.add_feature(crt.feature.OCEAN.with_scale('10m'), edgecolor='face', facecolor='white')
    # Format lat lon grid    
    gl = ax.gridlines(crs=crg, draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.yline = gl.xlines = True
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.ylabel_style = {'size': 12, 'color': 'gray'}
    gl.xlabel_style = {'rotation': 0, 'size': 12, 'color': 'gray'}
    gl.top_labels = gl.right_labels = False
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90.,91.,30))
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(-180.,181.,40))
    # plot names
    text_kws = dict(bbox=dict(color="none", zorder=101),color="k", fontsize=10,path_effects=[pe.withStroke(linewidth=2.5, foreground="w")],)
    regionmask.defined_regions.ar6.land.plot(ax=ax,text_kws=text_kws, add_ocean=False,label="abbrev")

    # colorbar
    ax.set_title("Reference regions with a secondary surge season", fontweight='bold', pad=14, fontsize=20)
    ax.text(-0.04, 1.05, 'b', transform=ax.transAxes, fontsize=20, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.2'))
    cbar= plt.colorbar(bs,ax=ax,orientation='vertical',shrink=0.9,pad=0.05)
    cbar.set_ticks(np.arange(clim[0],clim[1]))
    cbar.set_ticklabels(regionS)  
    cbar.ax.tick_params(labelsize=10)
ax.grid(True)
plot_dir= 'Paper1_plots/'
filename= 'IPCC_secondary_region.pdf'
plt.savefig(plot_dir + filename, dpi=600, format='pdf', bbox_inches='tight')
plt.show()

df_statS = pd.merge(dfS, Surge_filteredS['Surge_data'], left_index=True, right_index=True)
df_statS = df_statS.drop(columns={'Continent','geometry','Longitude', 'Latitude', 'bedlevel','index_right','Type'})#.sort_values(by='Name')
df_statS.keys()
Acronym = df_statS['Name'].unique()

df_melt_rel_biasS = pd.melt(df_statS[['Name','Surge_data','ivalue']],id_vars=['Name','ivalue'])
df_melt_rel_biasS['index'] = df_statS.index.copy()
df_melt_rel_biasS= df_melt_rel_biasS.set_index('index') 
df_melt_rel_biasS = df_melt_rel_biasS.drop(columns='variable').dropna()
df_melt_rel_biasS.keys()

df_melt_rel_bias_exploded2 = df_melt_rel_biasS.explode('value')

#%%%
First_season = ['N.W.North-America', 'N.E.North-America', 'W.North-America','E.North-America', 'N.Central-America', 'S.Central-America','Caribbean', 'N.W.South-America', 'N.South-America',
                'N.E.South-America', 'S.W.South-America','N.Europe', 'West&Central-Europe', 'Mediterranean', 'Sahara','Western-Africa', 'W.Southern-Africa', 'E.Southern-Africa', 'Madagascar', 
                'Russian-Arctic', 'Russian-Far-East', 'W.C.Asia','E.Asia', 'Arabian-Peninsula', 'S.Asia', 'S.E.Asia', 'N.Australia','C.Australia', 'S.Australia']

Second_season =  ['N.W.North-America', 'N.E.North-America', 'E.North-America', 'N.Central-America', 'S.Central-America', 'Caribbean','N.W.South-America','N.South-America',
                  'N.E.South-America', 'Mediterranean', 'Sahara', 'Western-Africa', 'Russian-Far-East', 'E.Asia', 'Arabian-Peninsula', 'S.Asia', 'S.E.Asia'] 

fig = plt.figure(figsize=(70, 80), tight_layout=True)
gs = fig.add_gridspec(6, 5)
labels = ['a1','a2','a3','a4','a5',
          'b1','b2','b3','b4','b5',
          'c1','c2','c3','c4','c5',
          'd1','d2','d3','d4','d5',
          'e1','e2','e3','e4','e5',
          'f1','f2','f3','f4']
plot_idx = 0  # To track subplot index

for region in First_season:
    ax = fig.add_subplot(gs[plot_idx // 5, plot_idx % 5])
    
    requirement1 = df_melt_rel_bias_exploded[df_melt_rel_bias_exploded['Name'] == region]
    current_region1 = requirement1['value']
    mean1 = current_region1.mean()
    std1 = current_region1.std()
    CV = std1/mean1 * 100
    skw1 = current_region1.skew()
    
    if region in Second_season:
        requirement2 = df_melt_rel_bias_exploded2[df_melt_rel_bias_exploded2['Name'] == region]
        current_region2 = requirement2['value']
        mean2 = current_region2.mean()
        std2 = current_region2.std()
        CV2 = std2/mean2 * 100
        skw2 = current_region2.skew()

        if not current_region1.empty:
            sns.histplot(current_region1,  bins=10, color='skyblue', stat='density', ax=ax, label=f'Primary season\nMean: {mean1:.2f}m \nCV: {CV:.2f}% \nSkew:{skw1:.2f}', zorder=2,alpha=0.5)
            sns.kdeplot(current_region1, color='skyblue', ax=ax, linewidth=3, zorder=4)  # Add KDE separately
        if not current_region2.empty:
            sns.histplot(current_region2, kde=True, bins=10, color='orange', stat='density', ax=ax, label=f'Secondary season\nMean: {mean2:.2f}m \nCV: {CV2:.2f}% \nSkew:{skw2:.2f}',zorder=1,alpha=0.5 )
            sns.kdeplot(current_region2, color='orange', ax=ax, linewidth=3, zorder=3)  # Add KDE separately
        
        ax.legend(fontsize=45, labelspacing=1.5,handleheight=2.0, loc='upper right') 
    else:
        if not current_region1.empty:
            sns.histplot(current_region1,  bins=10, color='skyblue', stat='density', ax=ax,label=f'Primary season\nMean: {mean1:.2f}m \nCV: {CV:.2f}% \nSkew:{skw1:.2f}',zorder=2,alpha=0.5 )
            sns.kdeplot(current_region1, color='skyblue', ax=ax, linewidth=3, zorder=4)
            ax.legend(fontsize=45, labelspacing=1.5,handleheight=2.0,  loc='upper right') 
    label_idx = plot_idx % len(labels)      
    ax.text(0.02, 0.98, labels[label_idx], fontsize=45,transform=ax.transAxes, verticalalignment='top',
            horizontalalignment='left',bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.3'))
    ax.set_title(f'{region}',fontsize=45)
    ax.set_xlabel('')  # Remove default label
    ax.set_ylabel('')
    ax.tick_params(axis='both', which='major', labelsize=40)
    plot_idx += 1
fig.text(0.5, -0.01, 'Surge peaks (m)', ha='center', fontsize=50)
fig.text(-0.01, 0.5, 'Density', va='center', rotation='vertical', fontsize=50)

plot_dir= 'Paper_plots/'
filename= 'regions.pdf'
plt.savefig(plot_dir + filename, dpi=600, format='pdf', bbox_inches='tight')
plt.tight_layout(pad=2.0)