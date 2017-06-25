# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 09:41:29 2017

@author: gerar
"""
import os
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#%%
def check_dir():
    tif_path = os.path.join(os.getcwd(),'TIF_Data')
    if os.path.exists(tif_path):
        os.chdir(tif_path)
    return [x for x in os.listdir(os.getcwd()) if x.endswith('.txt')]

def get_pd_table(data_file):
    data = pd.read_table(data_file, parse_dates=[0],infer_datetime_format = True)
    data = data.set_index('Date')
    data[data==-0.1]=np.nan
    return data

def interp_nan(pd_table):
    filled_table = pd_table.copy()
    data = np.array(filled_table['NDVI_data'])
    not_nan = np.logical_not(np.isnan(data))
    indices = np.arange(len(data))
    data = np.interp(indices, indices[not_nan], data[not_nan])
    filled_table['NDVI_data'] = data
    return filled_table    

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

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

def plot(pd_indata,pd_indata2=None,legend_name='NDVI Data',legend2=None,rmse = None, save = None):
    fig, axes = plt.subplots(figsize=(9,3))
 
    #Datos
    axes.plot(pd_indata.index,pd_indata['NDVI_data'],lw=.5,c='k',label='{}'.format(legend_name))
    if pd_indata2 is not None:
        axes.plot(pd_indata2.index,pd_indata2['NDVI_data'],lw=1,c='r',label='{}'.format(legend2))
    axes.legend(loc=2,numpoints=1,fontsize = 9,fancybox=True)
    if rmse is not None:
        axes.text(0.85,0.885,"RMSE={:.5f}".format(rmse[0]),fontsize=9,\
          transform=axes.transAxes)
    
    #Ajuste de eje
    axes.set_xlim([pd_indata.index.min(),pd_indata.index.max()])
    axes.set_ylim([pd_indata['NDVI_data'].min()-pd_indata['NDVI_data'].min(),pd_indata['NDVI_data'].max()+0.02])

    #Nombre de los ejes
    axes.set_xlabel("Fecha",fontsize=12)
    axes.set_ylabel("NDVI",fontsize=12)
    
    #Ajuste de figura
    fig.tight_layout()
    fig.autofmt_xdate()
    
    if save is not None:
        fig.savefig("{}_tseries.jpeg".format(legend2),dpi=1000,bbox_inches='tight')

def main():
    data_file = check_dir()[0]
    ndvi_data = interp_nan(get_pd_table(data_file))
    plot(get_pd_table(data_file))
    ndvi_filt = apply_savgol(ndvi_data,13,4)
#    plot(ndvi_filt,legend_name='Savitzky-Golay NDVI')
    plot(ndvi_data,ndvi_filt,legend2='Savitzky-Golay NDVI',rmse=rmse(ndvi_filt,ndvi_data),save=True)
    print 'RMSE inicial {}'.format(rmse(ndvi_filt,ndvi_data))
    w = get_weights(ndvi_filt,ndvi_data)
    w.columns = ['NDVI_data']
    for i in range(3):
        new_serie = create_new_serie(ndvi_filt,ndvi_data)
        new_serie_filt = apply_savgol(new_serie)
        fitting_index = abs(new_serie_filt-ndvi_data)*w
        print fitting_index.sum()
        ndvi_filt=new_serie_filt.copy()
    plot(ndvi_data,ndvi_filt,legend2='New Fitted serie',rmse=rmse(ndvi_filt,ndvi_data),save=True)
    print 'RMSE final {}'.format(rmse(ndvi_filt,ndvi_data))
    return ndvi_data, ndvi_filt
#%%
if __name__ == '__main__':
    a,b = main()