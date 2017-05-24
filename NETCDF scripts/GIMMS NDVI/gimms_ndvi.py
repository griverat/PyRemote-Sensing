# -*- coding: utf-8 -*-
"""
Created on Tue May 16 01:05:05 2017

@author: gerar
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
from osgeo import gdal,osr
import numpy as np
import os

#%%
def plot_data(data,cbar=0,save_img=0,name='image',norm = 0):
    plot,axs = plt.subplots()
    if norm == 1:
        norm = mpl.colors.Normalize(vmin=-0.5, vmax=0.5)
        cmap = mpl.cm.get_cmap('jet')
        raw_data = axs.imshow(data,interpolation="gaussian",cmap=cmap,norm=norm)
    else:
        raw_data = axs.imshow(data,interpolation="gaussian",cmap='Greens')
    if cbar == 1:
        cbar = plot.colorbar(raw_data)
    if save_img == 1:
        plt.savefig("{}.png".format(name),dpi=1000,bbox_inches='tight')
        
#%%
class Gdal_netcdf(object):
    def __init__(self,gdal_file):
        self.gdal_file = gdal.Open(gdal_file)
        self.sub_ds = self.gdal_file.GetSubDatasets()
        self.sds_ndvi = gdal.Open(self.sub_ds[0][0])
        
    def get_ndvi(self,subdataset,band_number):
        data = subdataset.GetRasterBand(band_number)
        no_data_value = data.GetMetadata()['ndvi_missing_value']
        fill_value = self.gdal_file.GetMetadata()['_fill_val']
        ndvi_data = data.ReadAsArray().astype(float)
        ndvi_data[np.where(ndvi_data == float(no_data_value))]=np.nan
        ndvi_data[np.where(ndvi_data == float(fill_value))]=np.nan
        return ndvi_data/10000
    
    def get_pixel_number(self,origin,resolution,coords):
        return np.abs(np.divide(np.subtract(coords,origin),resolution))
    
    def create_tiff(self,raster_band,raster_out,data,ul_lat,ul_lon,lr_lat,lr_lon):
        originX = float(raster_band.GetMetadata()['WesternmostLongitude'])
        originY = float(raster_band.GetMetadata()['NorthernmostLatitude'])
        cols = raster_band.RasterXSize
        rows = raster_band.RasterYSize
        pixelWidth = (max(
                float(raster_band.GetMetadata()['WesternmostLongitude']),
                float(raster_band.GetMetadata()['EasternmostLongitude']))-min(
                float(raster_band.GetMetadata()['WesternmostLongitude']),
                float(raster_band.GetMetadata()['EasternmostLongitude'])))/cols
        pixelHeight = -1*(max(
                float(raster_band.GetMetadata()['SouthernmostLatitude']),
                float(raster_band.GetMetadata()['NorthernmostLatitude']))-min(
                float(raster_band.GetMetadata()['SouthernmostLatitude']),
                float(raster_band.GetMetadata()['NorthernmostLatitude'])))/rows
        
        #Encuentro la ubicacion de las coordenadas en numero de pixel
        #para la caja definida por los lr/ul lat/lon
        y_ul, x_ul = self.get_pixel_number(
                (originY,originX),(pixelWidth,pixelHeight),
                (ul_lat,ul_lon))#(0,-82.5))
        y_lr, x_lr = self.get_pixel_number(
                (originY,originX),(pixelWidth,pixelHeight),
                (lr_lat,lr_lon))#(-20,-68))
        #Genero el tiff de salida
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(raster_out, int(x_lr-x_ul), int(y_lr-y_ul), 1, gdal.GDT_Float32)
        outRaster.SetGeoTransform((ul_lon, pixelWidth, 0, ul_lat, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(data[int(y_ul):int(y_lr),int(x_ul):int(x_lr)])
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()
    
    def main(self,offset=0):
        for band in range(1,self.sds_ndvi.RasterCount+1):
            ndvi_data = self.get_ndvi(self.sds_ndvi,band)
            self.create_tiff(self.sds_ndvi,
                             'ndvi_peru_band{}.tiff'.format(band+offset*12),
                             ndvi_data,0,-82.5,-20,-68)
#            break
    def stack_files(self,stack_out):
        geotiffs=[]
        for files in os.listdir(os.getcwd()):
            if files.endswith("tiff"):
                geotiffs.append(files)
        geotiffs.sort()
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(stack_out, int(x_lr-x_ul), int(y_lr-y_ul), 1, gdal.GDT_Float32)
        
    def del_variables(self):
        del self.gdal_file,self.sds_ndvi,self.sub_ds

#%%
if __name__ == '__main__':
    files_list = []
    for files in os.listdir(os.getcwd()):
        if files.endswith('.nc4'):
            files_list.append(files)
    for num,net_cdf in enumerate(files_list):
        temp = Gdal_netcdf(net_cdf)
        temp.main(num)
        temp.del_variables
        break
    
#     de 0 a -20 lat
#de -82.5 a -68 lon