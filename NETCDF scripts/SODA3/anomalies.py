#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 24 15:40:25 2017

@author: DangoMelon0701
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
from osgeo import gdal,osr
import numpy as np
import os

#%%
#Funcion de ayuda para visualizar los datos trabajados
def plot_data(data,cbar=0,save_img=0,name='image',norm = 0):
    plot,axs = plt.subplots()
    if norm == 1:
        norm = mpl.colors.Normalize(vmin=-0.5, vmax=0.5)
        cmap = mpl.cm.get_cmap('jet')
        raw_data = axs.imshow(data,interpolation="gaussian",cmap=cmap,norm=norm)
    else:
        raw_data = axs.imshow(data,interpolation="gaussian",cmap='jet')
    if cbar == 1:
        cbar = plot.colorbar(raw_data)
    if save_img == 1:
        plt.savefig("{}.png".format(name),dpi=1000,bbox_inches='tight')

#%%
#Esta clase calcula las anomalias del siguiente conjunto de ecuaciones
# x = x_clim + x~
# donde
# x_clim = [x]+<x> ; [x] = promedio y <x> = estacionalidad de la variable

class Anomalies(object):
    
    def __init__(self,gdal_netcdf):
        self.gdal_file = gdal.Open(gdal_netcdf)
        self.bandsn = self.gdal_file.RasterCount
        self.lines = self.gdal_file.RasterYSize
        self.samples = self.gdal_file.RasterXSize
        self.whole_data = np.zeros([self.bandsn,self.lines,self.samples])
        for band in range(1,self.bandsn+1):
            self.whole_data[band-1]=self.gdal_file.GetRasterBand(band).ReadAsArray()
        
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
    
    def save_tiff(self,data,raster_out="stacked_data.tif"):
        #Genero el tiff de salida
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(raster_out, self.samples, self.lines, self.bandsn, gdal.GDT_Float32)
        outRaster.SetGeoTransform(self.gdal_file.GetGeoTransform())
        for band in range(1,self.bandsn+1):
            outband = outRaster.GetRasterBand(band)
            outband.WriteArray(data[band-1])
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()
        del outRaster, outRasterSRS
    
    def end_anom(self):
        del self.gdal_file
#%%

if __name__ == '__main__':
    files_list=[]
    for files in os.listdir(os.getcwd()):
        if files.endswith(".nc"):
            files_list.append(files)
    for netcdf in files_list:
        calc = Anomalies(netcdf)
        calc.save_tiff(calc.get_anomalie(),raster_out='ptemp_stacked.tif')
        calc.end_anom()