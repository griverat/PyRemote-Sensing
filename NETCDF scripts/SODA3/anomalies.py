#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 24 15:40:25 2017

@author: Gerardo A. Rivera Tello
"""
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from scipy.io import netcdf
from osgeo import gdal,osr
import numpy as np
import os
#%%
if 'GDAL_DATA' not in os.environ:
    os.environ['GDAL_DATA'] = r'/home/DangoMelon0701/anaconda3/pkgs/libgdal-2.1.0-0/share/gdal'

#%%
# Funcion para plot en el mapa
def plot_map(data,lat,lon,band=None,title=None,savefig=None,name='image'):
    fig, axis = plt.subplots(figsize=(10,20))
    m = Basemap(projection = 'cyl', resolution = 'l',
                llcrnrlat=lat.min()-1,urcrnrlat=lat.max()+1,
                llcrnrlon=lon.min()-1, urcrnrlon=lon.max()+1)
    m.drawcoastlines(linewidth = 0.5)
    m.drawcountries()
    m.drawparallels(np.arange(-90.0,90.0,2.0), labels = [1,0,0,0])
    m.drawmeridians(np.arange(-180.0,180.0,2.0), labels = [0,0,0,0],linewidth=0.5)
    m.drawmeridians(np.arange(-180.0,180.0,10.0), labels = [0,0,0,1],linewidth=0.5)
    x, y =m(lon, lat)
    if band == None:
        mmap=m.pcolormesh(x, y, data, vmin=data.min(),vmax=data.max(),cmap=plt.cm.bwr)
    else:
        mmap=m.pcolormesh(x, y, data[band], vmin=data.min(),vmax=data.max(),cmap=plt.cm.bwr)
    cbar = m.colorbar(mmap,location='bottom',size='10%',pad='15%')
    cbar.set_label('°C')
    if title != None:
        axis.set_title(title)
    if savefig != None:
        fig.savefig("{}.png".format(name),dpi=1000,bbox_inches='tight')

#%%
#Esta clase calcula las anomalias del siguiente conjunto de ecuaciones
# x = x_clim + x~
# donde
# x_clim = [x]+<x> ; [x] = promedio y <x> = estacionalidad de la variable

class Anomalies(object):
    
    def __init__(self,data_netcdf):
        self.nc_file = netcdf.NetCDFFile(data_netcdf,'r')
        self.bandsn = self.nc_file.dimensions['time']
        self.lines = self.nc_file.dimensions['latitude']
        self.samples = self.nc_file.dimensions['longitude']
        self.whole_data = np.zeros([self.bandsn,self.lines,self.samples])
        self.lon,self.lat = np.meshgrid(self.nc_file.variables['longitude'][:],
                                        self.nc_file.variables['latitude'][:]) 
        self.temp = self.nc_file.variables['temp'][:,0]
        for band in range(1,self.bandsn+1):
            self.whole_data[band-1]=self.temp[band-1]
        
    def get_whole_mean(self):
        data_mean = np.zeros([self.lines,self.samples])
        for band in range(1,self.bandsn+1):
            data_mean +=self.whole_data[band-1]
        return data_mean/self.bandsn
    
    def get_seasonality(self,mean):
        season_data = np.zeros([12,self.lines,self.samples])
        global_diff = np.zeros([self.bandsn,self.lines,self.samples])
        for step in range(self.bandsn):
            global_diff[step]=self.whole_data[step]-mean            
        for month_number in range(12):
            for year in range(int(self.bandsn/12)):
                season_data[month_number] += global_diff[12*year+month_number]
            season_data[month_number] /= 10
        return season_data
    
    def get_climvalue(self,mean,seasonality):
        return mean+seasonality
    
    def get_anomalie(self):
        anomalie = np.zeros([self.bandsn,self.lines,self.samples])
        mean = self.get_whole_mean()
        climval = self.get_climvalue(mean,self.get_seasonality(mean))
        for year in range(1,int(self.bandsn/12)+1):
            anomalie[12*(year-1):12*year]=self.whole_data[12*(year-1):12*year]-climval
        return anomalie
    
    def get_anomalie_mean(self,anomalie):
        anomalie_mean = np.zeros([self.lines,self.samples])
        for band in range(self.bandsn):
            anomalie_mean +=anomalie[band]
        return anomalie_mean/self.bandsn
    
    def save_tiff(self,file,data,raster_out="stacked_data.tif"):
        #Genero el tiff de salida
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(raster_out, self.samples, self.lines, self.bandsn, gdal.GDT_Float32)
        gdal_file = gdal.Open(file)
        outRaster.SetGeoTransform(gdal_file.GetGeoTransform())
        for band in range(1,self.bandsn+1):
            outband = outRaster.GetRasterBand(band)
            outband.WriteArray(data[band-1])
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()
        del outRaster, outRasterSRS, gdal_file
    
    def end_anom(self):
        self.nc_file.close()
#%%

if __name__ == '__main__':
    files_list=[]
    for files in os.listdir(os.getcwd()):
        if files.endswith(".nc"):
            files_list.append(files)
    for f_netcdf in files_list:
        calc = Anomalies(f_netcdf)
        anom = calc.get_anomalie()
        anom_mean = calc.get_anomalie_mean(anom)
        calc.save_tiff(f_netcdf,anom,raster_out='ptemp_stacked.tif')
#%%
        plot_map(anom_mean,calc.lat,calc.lon,
                 title='Anomalies Mean from Jan2000 to Dec2009 - El Nino Zone 4',
                 savefig=1,name='mean_anomalies')
        plot_map(anom,calc.lat,calc.lon,band=0,
                 title='Potential Temperature Anomalie from Jan2000 - El Nino Zone 4',
                 savefig=1,name='anom_jan2000en4')
        plot_map(anom,calc.lat,calc.lon,band=24,
                 title='Potential Temperature Anomalies from Jan2002 - El Nino Zone 4',
                 savefig=1,name='anom_jan2002en4')
        calc.end_anom()