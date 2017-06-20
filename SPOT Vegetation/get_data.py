# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 01:12:48 2017

@author: Gerardo A. Rivera Tello
"""

from osgeo import gdal
import pandas as pd
import numpy as np
import os, sys, time, math

#%%
def get_data(lat,lon,tif_file):
    data = gdal.Open(tif_file)
    geoMatrix = data.GetGeoTransform()
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    lon_pixel = int(math.ceil(abs((lon - ulX) / xDist)))
    lat_pixel = int(math.ceil(abs((ulY - lat) / yDist)))
    ndvi = data.ReadAsArray()
    data = None
    return ndvi[lat_pixel][lon_pixel]*0.004-0.1

def check_dir():
    tif_path = os.path.join(os.getcwd(),'TIF_Data')
    if os.path.exists(tif_path):
        os.chdir(tif_path)

def main(user_lat,user_lon):
    check_dir()
    files = os.listdir(os.getcwd())
    num_files = len(files)
    ndvi_data = pd.DataFrame(index = np.arange(0,num_files),columns=('Date','NDVI_data'))
    print 'Comenzando lectura para la ubicacion ({},{})\n'.format(user_lat,user_lon)
    date_format = '%Y%m%d'
    for x,tif_file in enumerate(files):
        ndvi_data.loc[x] = [pd.to_datetime(tif_file[2:10],format = date_format),get_data(user_lat,user_lon,tif_file)]
        print 'Archivo {} leido'.format(tif_file)
    ndvi_data.set_index('Date',inplace=True)
    ndvi_data.to_csv('{}_{}_locdata.txt'.format(user_lat,user_lon),sep='\t')

#%%
if __name__ == '__main__':
    if len(sys.argv) > 3:
        print 'Ingrese solo dos argumentos\n Instrucciones de uso: python get_data.py LATITUDE LONGITUDE\n'
    else:
        start_time = time.time()
        main(float(sys.argv[1]),float(sys.argv[2]))
        print '\nProceso terminado en {} segundos\n'.format(round(time.time() - start_time,2))
    os.system("pause")