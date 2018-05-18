# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 02:27:52 2018

@author: Gerardo A. Rivera Tello
"""

import os, ujson, gdal, time, datetime
import numpy as np
import pandas as pd
from pyproj import Geod
from scipy import interpolate

#%%
def load_json(json_file):
    with open(json_file) as ofile:
        data_dict = ujson.load(ofile)
    return data_dict

#%%
def get_files(extension):
    files_list = [files for files in os.listdir(os.getcwd()) if files.endswith(extension)]
    return files_list

#%%
def padwithnan(vector, pad_width, iaxis, kwargs):
    vector[:pad_width[0]] = np.nan
    vector[-pad_width[1]:] = np.nan
    return vector

#%%
def get_sds(hdf):
    mod_file = gdal.Open(hdf)
    sds = mod_file.GetSubDatasets()
    _sds = [ name for name in sds if 'UNKNOWN' in name[0]]
    mod_file = None
    return _sds

#%%
def interp_nan(grid):
    x = np.arange(0, grid.shape[1])
    y = np.arange(0, grid.shape[0])
    grid = np.ma.masked_invalid(grid)
    xx, yy = np.meshgrid(x,y)
    x1 = xx[~grid.mask]
    y1 = yy[~grid.mask]
    new_grid = grid[~grid.mask]
    
    GD1 = interpolate.griddata((x1,y1),new_grid.ravel(),(xx,yy),method='linear')
    return GD1

#%%
def load_modis(hdf):
    ds_names = get_sds(hdf)
    strings = ['Latitude','Longitude', 'Scan_Start_Time (64-bit floating-point)']
    latlon_sds = [line[0] for line in ds_names if any(s in line[1] for s in strings)]
    lon_hdf = gdal.Open(latlon_sds[0])
    _lon = lon_hdf.ReadAsArray()
    lon_hdf = None
    lat_hdf = gdal.Open(latlon_sds[1])
    _lat = lat_hdf.ReadAsArray()
    lat_hdf = None
    time_hdf = gdal.Open(latlon_sds[2])
    _time = time_hdf.ReadAsArray()
    return _lat,_lon,_time

#%%
def get_data(sds):
    data_hdf = gdal.Open(sds)
    _data = data_hdf.ReadAsArray().astype(np.float)
    scale = data_hdf.GetRasterBand(1)
    scale = scale.GetScale()
    meta = data_hdf.GetMetadata()
    fill_val = float(meta['_FillValue'])
    _data[_data == fill_val] = np.nan
    data_hdf = None
    return _data*scale, meta

#%%
def calc_grid(data,x,y,dim):
    if dim != 1:
        subset = data[y-(dim/2):y+(dim/2+1),x-(dim/2):x+(dim/2+1)]
        is_nan = subset.size - np.count_nonzero(np.isnan(subset))
        if is_nan != 0:
            return np.nanmean(subset)
        else:
            return False
    elif ~np.isnan(data[y][x]):
        return data[y][x]
    else:
        return 'wat'

#%%
def get_distance(an_lon,an_lat,lon,lat):
    wgs84_geod = Geod(ellps="WGS84")
    return wgs84_geod.inv(an_lon,an_lat,lon,lat)[2]

#%%
def get_time(metadata,time,x,y):
    day = metadata['RANGEBEGINNINGDATE']
    passing_t = datetime.timedelta(seconds=time[y,x])
    fixed_t = datetime.datetime(1993,1,1)
    final_t = fixed_t+passing_t
#    mtime = metadata['RANGEBEGINNINGTIME'][0:5]
#    time_for_pixel = 300.0/(shape[0])
#    if "MOD" in sds:
#        passing_time = int(time_for_pixel*(shape[0]-(y+1))/60)
#    elif "MYD" in sds:
#        passing_time = int(time_for_pixel*(y+1)/60)
#    mtime = [int(t) for t in mtime.split(":")]
#    mtime[1] = mtime[1] + passing_time
#    if mtime[1] >= 60:
#        mtime[1] -= 60
#        mtime[0] += 1
#        end_time = ":".join([str(item).zfill(2) for item in mtime])
#    else:
#        end_time = ":".join([str(item).zfill(2) for item in mtime])
    return day, final_t.strftime('%X')

#%%
def get_qa(sds):
    qa = gdal.Open(sds)
    qa_data = qa.GetRasterBand(1).ReadAsArray()
    qa_data[qa_data != 3] = 0
    qa_data[qa_data != 0] = 1
    qa = None
    return qa_data
    
#%%
def main(aeronet_station,template,num):
    json_file = get_files('.json')
    st_data = load_json(json_file[0])
    st_data = st_data[aeronet_station]
    anlat = st_data['lat']
    anlon = st_data['lon']
#    df1 = pd.DataFrame(columns=['Date','Time','Data'])
#    df3 = df1.copy()
#    df5 = df1.copy()
    hdf_files = get_files('.hdf')
    with open("{}3x3_MODIS.txt".format(aeronet_station),"w") as file3x3_end:
        for hdf in hdf_files:
            sds = template.format(hdf,num)
            lat,lon, time = load_modis(hdf)
            if not (lat.min()<anlat<lat.max()) or not (lon.min()<anlon<lon.max()):
                continue
            if lat[lat==-999.].size != 0:
                lat[lat==-999.]=np.nan
                lat=lat[~np.isnan(lat).any(axis=1)]
                lon[lon==-999.]=np.nan
                lon=lon[~np.isnan(lon).any(axis=1)]
    #            lat[lat==-999.] = np.nan
    #            lat = interp_nan(lat)
    #            lon[lon==-999.] = np.nan
    #            lon = interp_nan(lon)
            dist = get_distance(np.full(lon.shape,anlon),np.full(lat.shape,anlat),lon,lat)
#            data, meta = get_data(sds)
#            giov = np.nanmean(data[np.where(dist<=27500)])
                        
#            if ~np.isnan(giov):
#                fileGio_end.write("{}\t{}\t{}\n".format(day,end_time,giov))
            
            if dist.min() >  7101 :
#                del data, meta, dist, giov
                continue
            data, meta = get_data(sds)
            if 'L2' in hdf and num == 52 or num == 66:
                qa = get_qa(template.format(hdf,61))
                data *=qa
                data[data==0.]=np.nan
            y,x = np.unravel_index(dist.argmin(),dist.shape)
            day, end_time = get_time(meta,time,x,y)
            
            data = np.pad(data,2,padwithnan)
            x += 2
            y += 2
            v3 = calc_grid(data,x,y,3)
#            df1 = df1.append({'Date':day,'Time':end_time,'Data':v1},ignore_index=True)
#            df3 = df3.append({'Date':day,'Time':end_time,'Data':v3},ignore_index=True)
#            df5 = df5.append({'Date':day,'Time':end_time,'Data':v5},ignore_index=True)
            if v3 != False:
                file3x3_end.write("{}\t{}\t{}\n".format(day,end_time,v3))
                print 'Done {}\n'.format(hdf)
                
#        df1.to_csv('{}1x1_MODIS.txt'.format(aeronet_station),header=None,index=None,sep='\t')
#        df3.to_csv('{}3x3_MODIS.txt'.format(aeronet_station),header=None,index=None,sep='\t')
#        df5.to_csv('{}5x5_MODIS.txt'.format(aeronet_station),header=None,index=None,sep='\t')

#%%
if __name__ == '__main__':
    start_time = time.time()
    file_template = 'HDF4_SDS:UNKNOWN:{}:{}'
    main('lapaz',file_template,12)
    print "--- {} seconds --- \n".format(round(time.time() - start_time,2))
    os.system("pause")