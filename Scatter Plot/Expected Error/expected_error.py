# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 10:55:39 2017

@author: gerar
"""

import os
import numpy as np
import pandas as pd

#%%
#Datos de la estacion
AERONET_station = "Rio Branco"

#%%
#Cantidad de pixeles a tomar en promedio
grid = "5x5"

#%%
#Encuentro el archivo en formato txt a plottear
file_to_plot = [x for x in os.listdir(os.getcwd()) \
               if x.endswith("{}{}_matched_data.txt".format(\
                             AERONET_station.lower().replace(" ",""),grid))]
#Abro el archivo y guardo los datos en numpy.arrays (dtype=float)
modis_data,aeronet_data = np.loadtxt(file_to_plot[0],skiprows = 1,usecols=(2,4),unpack=True)

#Leo la data para graficar una serie de tiempo
data = pd.read_table(file_to_plot[0], parse_dates=[0],infer_datetime_format = True) 

print "Archivo Leido\nProcesando los errores esperados..."
np.seterr(all='ignore')
#%%
#Realizo los calculos del EE
_ee = np.abs(0.05 + 0.15*aeronet_data)
ee_plus = aeronet_data + _ee
ee_minus = aeronet_data - _ee

#1- Dentro del EE:
within_ee = data[np.logical_and(ee_minus<modis_data,modis_data<ee_plus)]
within_ee.to_csv('{}{}_dentro-ee.txt'.format(AERONET_station.lower().replace(" ",""),grid),index = None, sep='\t')
#2- Por encima del EE:
above_ee = data[ee_plus<modis_data]
above_ee.to_csv('{}{}_encima-ee.txt'.format(AERONET_station.lower().replace(" ",""),grid),index = None, sep='\t')

#3- Por debajo del EE:
below_ee = data[modis_data<ee_minus]
below_ee.to_csv('{}{}_debajo-ee.txt'.format(AERONET_station.lower().replace(" ",""),grid),index = None, sep='\t')