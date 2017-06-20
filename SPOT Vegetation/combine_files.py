#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 16:21:06 2017

@author: Gerardo A. Rivera Tello
"""
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib as mpl
from osgeo import gdal,osr
import numpy as np
import os

#%%
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
def metadata_as_dict(metadata_txt):
    print "\nComenzando la lectura del metadato"
    meta = {}
    with open(metadata_txt) as txt:
        for line in txt:
            (key, val) = line.split(None,1)
            meta[key] = val[:-1]
    print "Terminado\n"
    return meta

def filter_cloud_flag(quality):
    print "Computando la mascara de nubes"
    flags = gdal.Open(quality).ReadAsArray()
    cloud_mask = flags & 3
    land = flags & 8
    land = np.abs(land-cloud_mask)/8
    flags = None
    print "Terminado\n"
    return land
    
def create_tiff(raster_out,meta,data,quality):
    driver = gdal.GetDriverByName('GTiff')
    res = float(meta['MAP_PROJ_RESOLUTION'])
    outRaster = driver.Create(raster_out, data.shape[1], data.shape[0], 1, gdal.GDT_Byte,['INTERLEAVE=BAND'])
    outRaster.SetGeoTransform((float(meta['CARTO_UPPER_LEFT_X'])-res/2, res, 0, float(meta['CARTO_UPPER_LEFT_Y'])+res/2, 0, -res))
    outband = outRaster.GetRasterBand(1)
    data *= quality
    outband.WriteArray(data)
    outband.SetDescription('NDVI_DATA')
    outRaster.SetMetadata(meta)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()
        
def main(data_hdf,quality_hdf,metadata_txt,path=os.getcwd()):
    data = gdal.Open(data_hdf).ReadAsArray().astype(np.int)
#    data = data*0.004-0.1
    create_tiff(os.path.join(path,'{}.tif'.format(data_hdf[:-8])),metadata_as_dict(metadata_txt),data,filter_cloud_flag(quality_hdf))
    print 'GeoTIFF generado'    
    data = None
#%%
if __name__ == '__main__':
    dir_files = [files for files in os.listdir(os.getcwd())]
    hdf_files = [hdf for hdf in dir_files if hdf.endswith('.HDF')]
    txt_files = [txt for txt in dir_files if txt.endswith('_LOG.TXT')]
    if 'NDV' in hdf_files[0]:
        main(hdf_files[0],hdf_files[1],txt_files[0])
    else:
        main(hdf_files[1],hdf_files[0],txt_files[0])