#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  7 08:37:55 2017

@author: Gerardo A. Rivera Tello
"""
import numpy as np
from struct import unpack

#%%
#Defino una funcion que me permitira leer el bin por bloques
def read_chunk(data,offset,n_elements,data_type):
    '''
    Read the data decoded inside of the file object data. 
    It returns a tuple containing the type of data specified 
    '''
    data.seek(offset)
    rdata = data.read(n_elements)
    return unpack(data_type,rdata)[0]
#%%
#Defino una funcion que me ayudara a manejar los datos leidos
def npread_data(data,offset,n_elements,np_type):
    data.seek(offset)
    rdata = np.fromfile(data,dtype=np_type,count=n_elements)
    return rdata

#%%
with open('sst.bin','rb') as in_bin:
    initial_offset=0
    for t_steps in range(1000):
        try:
            #Cada linea de data contiene una fila, por lo que 720 lecturas
            #corresponderan a un solo dia
            for lines in range(720):
                #El primer elemento lo leo como int - 4 bytes. Este primer elemento
                #contiene informacion sobre la cantidad de bytes que compone la data
                inum_bytes_data = read_chunk(in_bin,initial_offset,4,'i')
                
                #De antemano conozco que mi archivo bin contiene data tipo
                #double precision float - 8 bytes (este es el tipo de dato en el
                #que ferret guarda sus archivos binarios para versiones >v6.8)
                #por lo que el resto del archivo lo leere de esa forma
    
                real_data = npread_data(in_bin,initial_offset+4,int(inum_bytes_data/8),np.float64)
                
                #Por ultimo los 4 bytes siguientes a la data se leeran como int - 4 bytes
                #Es el mismo valor leido al comienzo. Siempre va uno antes y despues
                #de la data
                fnum_bytes_data = read_chunk(in_bin,initial_offset+inum_bytes_data+4,4,'i')
                
                initial_offset = (t_steps*720+lines+1)*(8+inum_bytes_data)
        except:
            print("\nEl numero de pasos de tiempo es {}".format(t_steps))
            break