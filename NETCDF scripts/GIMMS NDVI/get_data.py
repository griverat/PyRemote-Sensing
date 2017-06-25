# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 00:00:06 2017

@author: gerar
"""

from osgeo import gdal
import pandas as pd
import numpy as np
import os, sys, time, math, re

#%%
def get_data(lat,lon,tif_file):
    data = gdal.Open(tif_file)
    geoMatrix = data.GetGeoTransform()
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    lon_pixel = int(math.ceil(round(abs((lon - ulX) / xDist),5)))
    lat_pixel = int(math.ceil(round(abs((ulY - lat) / yDist),5)))
    ndvi = data.ReadAsArray()
    data = None
    return ndvi[lat_pixel][lon_pixel]

def check_dir():
    tif_path = os.path.join(os.getcwd(),'TIF_Data')
    if os.path.exists(tif_path):
        os.chdir(tif_path)

def natural_sort(files_list): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)] 
    return sorted(files_list, key=alphanum_key)

def main(user_lat,user_lon):
    check_dir()
    files = natural_sort([x for x in os.listdir(os.getcwd()) if x.endswith('.tif')])
    num_files = len(files)
    ndvi_data = pd.DataFrame(index = np.arange(0,num_files),columns=('Date','NDVI_data'))
    dates = pd.date_range('1981-07-01','2015-12-31',freq='SM')
    print 'Comenzando lectura para la ubicacion ({},{})\n'.format(user_lat,user_lon)
    for x,tif_file in enumerate(files):
        ndvi_data.loc[x] = [dates[x],get_data(user_lat,user_lon,tif_file)]
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