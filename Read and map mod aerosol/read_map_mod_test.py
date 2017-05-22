# -*- coding: utf-8 -*-
"""
Created on Sun Dec 04 11:35:47 2016

@author: gerar
"""

#%%
#Importo las librerias necesarias

import gdal
import os
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import sys

#%%
#Defino mis variables globales
files_list = []
file_template = 'HDF4_{}:{}:{}:{}'

#%%
#Procedo a guardar todos los archivos.hdf en mi contenedor
try:
    for files in os.listdir(os.getcwd()):
        if files.endswith(".hdf"):
            files_list.append(files)

#Error a mostrar en caso no encuentre archivos con la extension
except:
    print('No se encontro archivos con la extensión .hdf en el \
    diretorio de trabajo')
    sys.exit()

#%%
for file_name in files_list:
    user_input=raw_input('\nDesea procesar\n {} \n\n(Y/N)'.format(file_name))
    if(user_input.lower() == 'n'):
        continue
    else:
        #Diferencio si es una modis 3k o 10k
        if "3K" in file_name:
            print "Este es un archivos MODIS 3K"
            sds_name = "mod04:Optical_Depth_Land_And_Ocean"
            _aod = file_template.format("EOS","EOS_SWATH",file_name,sds_name)
            _lat = file_template.format("SDS","UNKNOWN",file_name,1)
            _lon = file_template.format("SDS","UNKNOWN",file_name,0)
            
        elif "L2" in file_name:
            print "Este es un archivo MODIS 10k"
            sds_name = "mod04:Optical_Depth_Land_And_Ocean"
#            sds_name = "mod04:AOD_550_Dark_Target_Deep_Blue_Combined"
#            sds_name = "mod04:Deep_Blue_Aerosol_Optical_Depth_550_Land"
#            sds_name = "mod04:Effective_Optical_Depth_0p55um_Ocean"
            _aod = file_template.format("EOS","EOS_SWATH",file_name,sds_name)
            _lat = file_template.format("SDS","UNKNOWN",file_name,1)
            _lon = file_template.format("SDS","UNKNOWN",file_name,0)
            
        else:
            print "El archivo {} no es un fichero MODIS valido\n(O esta\
            nombrado de manera incorrecta)".format(file_name)
            continue
#%%
        #Esta secuencia del for sera para abrir el archivo hdf y extraer los datos
        try:
            hdf = gdal.Open(file_name)
        except:
            print "No es posible abrir el archivo \n {} \n Saltando...".format(file_name)
            continue
        #Obtengo los valores de latitud ,longitud y aod
        #1- Latitud
        lat = gdal.Open(_lat)
        latitude = lat.ReadAsArray()
        min_lat = latitude.min()
        max_lat = latitude.max()
        
        #2- Longitud
        lon = gdal.Open(_lon)
        longitude = lon.ReadAsArray()
        min_lon = longitude.min()
        max_lon = longitude.max()

        #3- AOD
        try:
            sds = gdal.Open(_aod)
        except:
            print "Disculpe, su archivo MODIS hdf no contiene la SDS llamada {}".format(sds_name)
            sys.exit()
        #Obtenemos el factor de escala para la SDS del AOD
        raster_band = sds.GetRasterBand(1)
        scale = raster_band.GetScale()
        
        #Obtenermos la data del AOD
        data = sds.ReadAsArray()
#%%
        #Obtenemos los datos en un rango valido filtrando los negativos
        passer = np.logical_and(data > 0 , data <= data.max())
        valid_data = data[passer]*scale
        #Mostramos la información
        print "\nEl rango valido de la data es: {} hasta {}\nEl promedio es:\
        {}\nLa desviacion estandar es: {}".format(valid_data.min(),\
        valid_data.max(),valid_data.mean(),valid_data.std())
        print "El rango de la latitud en este archivo es: de {} hasta {} grados\
        \nEl rango de la longitus en este archivo es: de {} hasta {} \
        grados".format(min_lat,max_lat,min_lon,max_lon)

#%%
        #Preguntamos al usuario si desea visualizar un mapa
        is_map = raw_input("\nDesearia crear un mapa de esta data?\
        \nIntroduzca Y o N: \n")
        #En caso de ser si, plottear el mapa
        if is_map.lower() == "y":
            data = data.astype(float)
            data[data==-9999] = np.nan
            data = np.ma.masked_array(data, np.isnan(data))
            m = Basemap(projection = 'cyl', resolution = 'l', llcrnrlat=min_lat\
                        ,urcrnrlat=max_lat, llcrnrlon=min_lon, urcrnrlon=max_lon)
            m.drawcoastlines(linewidth = 0.5)
            m.drawcountries()
            m.drawparallels(np.arange(-90.0,91.0,5.0), labels = [1,0,0,0])
            m.drawmeridians(np.arange(-180.0,181.0,5.0), labels = [0,0,0,1])
            x, y =m(longitude, latitude)
            m.pcolormesh(x, y, data*scale, vmin=0,vmax=1)
            plt.autoscale()
            
            #Creamos la barra de colores
            cb = m.colorbar()
            #Etiqueta del colorbar
            cb.set_label("AOD")
            
            #Titulo del grafico
            plotTitle = file_name[:-4]
            plt.title("{}\n {}".format(plotTitle, sds_name[6:]))
            fig = plt.gcf()
            fig.savefig("{}_map.jpeg".format(sds_name[6:]),dpi=1000)
            
            #Muestro la ventada con el grafico
            plt.show()
            break