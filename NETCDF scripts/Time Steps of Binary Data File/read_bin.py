#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  6 21:53:21 2017

@author: Gerardo A. Rivera Tello
"""
import numpy as np
import matplotlib.pyplot as plt

#%%
def plot_data(data,cbar=0,save_img=0):
    plot,axs = plt.subplots()
    raw_data = axs.imshow(data,interpolation="gaussian",cmap='jet')
    if cbar == 1:
        cbar = plot.colorbar(raw_data)
    if save_img == 1:
        plt.savefig("diplay_of_bytes.png",dpi=500,bbox_inches='tight')


#%%
num_lines = 23
num_samples = 84
time_interval = 96
#Abro el archivo para extraer los datos
with open('oscar.bin','rb') as in_bin:
    #Matriz contenedora de los datos leidos
    array = np.zeros([time_interval,num_lines,num_samples])
    data = np.fromfile(in_bin,dtype=np.float32)
    for t in range(time_interval):
        for i in range(num_lines):
            for j in range(num_samples):
                array[t][abs(i-num_lines+1)][j]=data[(t*num_samples*num_lines+2*t+1)+(i*num_samples)+j]
#    array = np.reshape(data[:,1:-1],[time_interval,num_lines*num_samples])
    
#%%

plot_data(array[0],1)