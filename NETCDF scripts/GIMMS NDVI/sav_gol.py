# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 09:41:29 2017

@author: gerar
"""
import os
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import pandas as pd
#import numpy as np

#%%
def check_dir():
    tif_path = os.path.join(os.getcwd(),'TIF_Data')
    if os.path.exists(tif_path):
        os.chdir(tif_path)
    return [x for x in os.listdir(os.getcwd()) if x.endswith('.txt')]

def get_pd_table(data_file):
    data = pd.read_table(data_file, parse_dates=[0],infer_datetime_format = True)
    data = data.set_index('Date')
    return data
    
def apply_savgol(pd_dataframe,window=9,poly=6):
    pd_dataframecopy = pd_dataframe.copy()
    pd_dataframecopy['NDVI_data']=savgol_filter(pd_dataframecopy['NDVI_data'],window,poly,mode='wrap')
    return pd_dataframecopy

def get_weights(fitted_serie,original_serie):
    d = abs(original_serie-fitted_serie)
    weight = original_serie.copy()
    weight[original_serie>=fitted_serie] = 1
    weight[original_serie<fitted_serie] = 1-d[original_serie<fitted_serie]/d[original_serie<fitted_serie].max()
    weight.columns = ['Weights']
    return weight

def create_new_serie(fitted_serie, original_serie):
    new_serie = original_serie.copy()
    new_serie[original_serie<fitted_serie] = fitted_serie[original_serie<fitted_serie]
    return new_serie

def plot(pd_indata,pd_indata2=None,legend_name='NDVI Data',legend2=None):
    fig, axes = plt.subplots(figsize=(9,3))
 
    #Datos
    axes.plot(pd_indata.index,pd_indata['NDVI_data'],lw=.5,c='k',label='{}'.format(legend_name))
    if pd_indata2 is not None:
        axes.plot(pd_indata2.index,pd_indata2['NDVI_data'],lw=1,c='r',label='{}'.format(legend2))
    axes.legend(loc=9,numpoints=1,fontsize = 9,fancybox=True)
    
    #Ajuste de eje
    axes.set_xlim([pd_indata.index.min(),pd_indata.index.max()])
    axes.set_ylim([pd_indata['NDVI_data'].min()-0.02,pd_indata['NDVI_data'].max()+0.02])

    #Nombre de los ejes
    axes.set_xlabel("Fecha",fontsize=12)
    axes.set_ylabel("NDVI",fontsize=12)
    
    #Ajuste de figura
    fig.tight_layout()
    fig.autofmt_xdate()

def main():
    data_file = check_dir()[0]
    ndvi_data = get_pd_table(data_file)
#    plot(ndvi_data)
    ndvi_filt = apply_savgol(ndvi_data,15,4)
#    plot(ndvi_filt,legend_name='Savitzky-Golay NDVI')
    plot(ndvi_data,ndvi_filt,legend2='Savitzky-Golay NDVI')
    w = get_weights(ndvi_filt,ndvi_data)
    w.columns = ['NDVI_data']
    for i in range(2):
        new_serie = create_new_serie(ndvi_filt,ndvi_data)
        new_serie_filt = apply_savgol(new_serie)
        fitting_index = abs(new_serie_filt-ndvi_data)*w
        print fitting_index.sum()
        ndvi_filt=new_serie_filt.copy()
    plot(ndvi_data,ndvi_filt,legend2='New Fitted serie')
    return ndvi_data, ndvi_filt
#%%
if __name__ == '__main__':
    a,b = main()