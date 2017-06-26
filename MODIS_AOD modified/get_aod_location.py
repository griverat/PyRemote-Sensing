# -*- coding: utf-8 -*-
"""
Created on Mon Dec 05 09:25:08 2016

@author: gerar
"""

#%%
#Importo las librerias necesarias
import os
import sys
import numpy as np
import gdal
import time

#%%
#Defino mis variables globales
start_time = time.time()
files_list = []
file_template = 'HDF4_{}:{}:{}:{}'
location = "riobranco"
sds_name = "mod04:Optical_Depth_Land_And_Ocean"
szenith_sds = "mod04:Solar_Zenith"
#sds_name = "mod04:AOD_550_Dark_Target_Deep_Blue_Combined"
loc_dic = {"huancayo":(-12.04020,-75.32090),"riobranco":(-9.95747,-67.86935),"lapaz":(-16.53900,-68.06647),"arica":(-18.47167,-70.31333),"medellin":(6.26067,-75.57791)}

#%%
#Encuentro la latitud y longitud correspondiente a la estacion
if location in loc_dic:
    user_lat = loc_dic[location][0]
    user_lon = loc_dic[location][1]
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
#Bucle sobre los archivos en mi lista
#Obtengo los nombres de las SDS
with open("{}5x5_MODIS.txt".format(location),"a") as file_end, open("{}3x3_MODIS.txt".format(location),"a") as file3x3_end, open("{}1x1_MODIS.txt".format(location),'a') as file1x1_end:
    for file_name in files_list:
        _aod = file_template.format("EOS","EOS_SWATH",file_name,sds_name)
        _szenith = file_template.format("EOS","EOS_SWATH",file_name,szenith_sds)
        _lat = file_template.format("SDS","UNKNOWN",file_name,1)
        _lon = file_template.format("SDS","UNKNOWN",file_name,0)
        
#%%
        #Esta secuencia del for sera para abrir el archivo hdf y extraer los datos
        try:
            hdf = gdal.Open(file_name)
            del hdf
        except:
            print "No es posible abrir el archivo \n {} \n Saltando...".format(file_name)
            continue
        #Obtengo los valores de latitud ,longitud
        #1- Latitud
        lat = gdal.Open(_lat)
        latitude = lat.ReadAsArray()
        min_lat = latitude.min()
        max_lat = latitude.max()
        del lat
        
        #2- Longitud
        lon = gdal.Open(_lon)
        longitude = lon.ReadAsArray()
        min_lon = longitude.min()
        max_lon = longitude.max()
        del lon

#%%
        #Esta secuencia revisara si la longitud y latitud de la estación estan
        #en rango para el .hdf
        if not min_lat<user_lat<max_lat or not min_lon<user_lon<max_lon:
            del sds
            continue
#%%    
        #Esta parte lee el valor del angulo zenith luego de haber comprobado
        #que la lat/lon esta dentro del archivo
        
        # Angulo zenith
        try:
            szenith = gdal.Open(_szenith)
        except:
            print "Disculpe, su archivo MODIS hdf no contiene la SDS llamada {}".format(szenith_sds)
            sys.exit()
        solar_zenith = szenith.ReadAsArray()
        szenih_scale = szenith.GetRasterBand(1).GetScale()
        del szenith
        
            
        #AOD
        try:
            sds = gdal.Open(_aod)
        except:
            print "Disculpe, su archivo MODIS hdf no contiene la SDS llamada {}".format(sds_name)
            sys.exit()
            
        #Obtenermos la data del AOD
        data = sds.ReadAsArray()
        #Realizo un pad al array de 2 para poder promediar en una caja de 5x5
        def padwithnan(vector, pad_width, iaxis, kwargs):
            vector[:pad_width[0]] = np.nan
            vector[-pad_width[1]:] = np.nan
            return vector
        data = np.pad(data,2,padwithnan)
        solar_zenith = np.pad(solar_zenith,2,padwithnan)
        
        #Obtenemos el factor de escala para la SDS del AOD
        scale = float(sds.GetMetadata()['scale_factor'])
    
        fill_value = sds.GetMetadata()['_FillValue']
    
#%%
        #Calcularemos el punto más cercano a la latitud y longitud ingresadas
        #usando la formula de haversines
        R = 6372.8 #radio de la tierra en kilometros
        lat1 = np.radians(user_lat)
        lat2 = np.radians(latitude)
        delta_lat = np.radians(latitude - user_lat)
        delta_lon = np.radians(longitude - user_lon)
        a=(np.sin(delta_lat/2))**2+(np.cos(lat1))*(np.cos(lat2))*(np.sin(delta_lon/2))**2
        c=2*np.arcsin(np.sqrt(a))
        d=R*c
    
#%%
        #Una vez calculado el np.array con los valores de distancia
        #buscaremos el minimo junto al indice
        x,y=np.unravel_index(d.argmin(),d.shape)
    
#%%
        #Si la distancia es menor a 7.07km, obviamos el pixel
        if d[x,y] > 20:
            del sds
            continue
#%%
        #Obtengo la hora de inicio del escaneo
        day = sds.GetMetadata()['RANGEBEGINNINGDATE']
        mtime = sds.GetMetadata()['RANGEBEGINNINGTIME'][0:5]
        #la hora a la que pasa por el pixel
        time_for_pixel = 300.0/(len(latitude))
        if "MOD" in file_name:
            passing_time = int(time_for_pixel*(len(latitude)-(x+1))/60)
        elif "MYD" in file_name:
            passing_time = int(time_for_pixel*(x+1)/60)
        mtime = [int(t) for t in mtime.split(":")]
        mtime[1] = mtime[1] + passing_time
        if mtime[1] >= 60:
            mtime[1] -= 60
            mtime[0] += 1
            end_time = ":".join([str(item).zfill(2) for item in mtime])
        else:
            end_time = ":".join([str(item).zfill(2) for item in mtime])
    
#%%

        x +=2
        y +=2
        #Se calcula el promedio en una grilla de 5x5
        five_by_five = data[x-2:x+3,y-2:y+3]
        fbf_zenith = solar_zenith[x-2:x+3,y-2:y+3]
        five_by_five = five_by_five.astype(float)
        fbf_zenith = fbf_zenith.astype(float)
        five_by_five[five_by_five<0.0] = np.nan
        five_by_five[five_by_five == float(fill_value)] = np.nan
        # en una grilla de 3x3
        three_by_three = np.copy(five_by_five[1:4,1:4])
        tbt_zenith = np.copy(fbf_zenith[1:4,1:4])
        #y de 1x1
        one_by_one = three_by_three[1][1]
        obo_zenith = tbt_zenith[1][1]
        
        __nnan = np.count_nonzero(~np.isnan(one_by_one))
        _nnan = np.count_nonzero(~np.isnan(three_by_three))
        nnan = np.count_nonzero(~np.isnan(five_by_five))
        if nnan == 0:
            del sds
            continue
        else:
            if _nnan == 0:
                del _nnan
                del __nnan
            else:
                if __nnan ==0:
                    del __nnan
                else:
                    one_by_one *= scale
                    obo_zenith *= szenih_scale
                    if one_by_one > 0 :
                        file1x1_end.write("{}\t{}\t{}\t{}\n".format(day,end_time,one_by_one,obo_zenith))
                three_by_three *= scale
                tbt_zenith *= szenih_scale
                three_by_three_avrg = np.nanmean(three_by_three)
                tbt_zenith_avrg = np.nanmean(tbt_zenith)
                if three_by_three_avrg > 0 :
                    file3x3_end.write("{}\t{}\t{}\t{}\n".format(day,end_time,three_by_three_avrg,tbt_zenith_avrg))
            five_by_five *= scale
            fbf_zenith *= szenih_scale
            five_by_five_avrg = np.nanmean(five_by_five)
            fbf_zenith_avrg = np.nanmean(fbf_zenith)
            if five_by_five_avrg >0:
                file_end.write("{}\t{}\t{}\t{}\n".format(day,end_time,five_by_five_avrg,fbf_zenith_avrg))
                print "Done {}".format(file_name)
                del sds

print "--- {} seconds --- \n".format(round(time.time() - start_time,2))
os.system("pause")