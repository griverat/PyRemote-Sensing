# -*- coding: utf-8 -*-
"""
Created on Mon May 07 17:34:56 2018

@author: gerar
"""

import os
import pandas as pd
import numpy as np
from scipy.stats.stats import pearsonr

#%%
def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

#%%
def mae(predictions,targets):
    return np.abs((predictions - targets)).mean()

#%%
def bias(predictions,targets):
    return np.mean(predictions)-np.mean(targets)

#%%
def r_deming(x,y):
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    sxx = np.sum(np.power(x-x_mean,2.))/(len(x)-1.)
    syy = np.sum(np.power(y-y_mean,2.))/(len(x)-1.)
    sxy = np.sum((x-x_mean)*(y-y_mean))/(len(x)-1.)
    lamb = np.var(y)/np.var(x)
    b1 = (syy-lamb*sxx+np.sqrt((syy-lamb*sxx)**2 +4*lamb*sxy**2))/(2*sxy)
#    b0 = y_mean - x_mean*b1
    return b1
 
#%%
def get_data(_file):
#    data = pd.read_table(file_to_plot[0], parse_dates=[0],infer_datetime_format = True,usecols=(0,2,4)) #, parse_dates=[0],infer_datetime_format = True
#    data = data.dropna() #[pd.notnull(data['AOD_AERONET'])]
#    data = data.set_index('Date_MODIS')
    modis_data,aeronet_data = np.loadtxt(_file,skiprows = 1,usecols=(2,4),unpack=True)    
    return modis_data, aeronet_data

#%%
def helper(x):
    return pd.DataFrame({'AOD_MODIS':x['AOD_MODIS'].values,'AOD_AERONET':x['AOD_AERONET'].values})

#%%
def main():
    files = [x for x in os.listdir(os.getcwd()) if x.endswith("matched_data_end.txt")]
    for _file in files:
        modis, aeronet = get_data(_file)
        general_data = pd.DataFrame(columns=['Statistics'],index=['RMSE','R_deming','R_pearson','MAE','BIAS','MEAN_MODIS','MEAN_AERONET'])
        general_data.loc['RMSE']=rmse(modis,aeronet)
        general_data.loc['R_deming']=r_deming(modis,aeronet)
        general_data.loc['R_pearson']=pearsonr(modis,aeronet)[0]
        general_data.loc['MAE']=mae(modis,aeronet)
        general_data.loc['BIAS']=bias(modis,aeronet)
        general_data.loc['MEAN_MODIS']=np.mean(modis)
        general_data.loc['MEAN_AERONET']=np.mean(aeronet)
        
        data = pd.read_table(_file,usecols=[0,2,4])
        data['Date_MODIS'] = data['Date_MODIS'].astype('datetime64[ns]')
        m_data = data.groupby([data['Date_MODIS'].dt.month]).apply(helper)
        m_index = m_data.index.get_level_values(0).unique()
        
        m_end = pd.DataFrame(columns=m_index,index=['RMSE','R_deming','R_pearson','MAE','BIAS','MEAN_MODIS','MEAN_AERONET'])
        for values in m_index:
            month_Data = m_data.loc[values]
            if len(month_Data)==1:
                continue
            m_end.loc['RMSE'][values]=rmse(month_Data['AOD_MODIS'],month_Data['AOD_AERONET'])
            m_end.loc['R_deming'][values]=r_deming(month_Data['AOD_MODIS'],month_Data['AOD_AERONET'])
            m_end.loc['R_pearson'][values]=pearsonr(month_Data['AOD_MODIS'],month_Data['AOD_AERONET'])[0]
            m_end.loc['MAE'][values]=mae(month_Data['AOD_MODIS'],month_Data['AOD_AERONET'])
            m_end.loc['BIAS'][values]=bias(month_Data['AOD_MODIS'],month_Data['AOD_AERONET'])
            m_end.loc['MEAN_MODIS'][values]=np.mean(month_Data['AOD_MODIS'])
            m_end.loc['MEAN_AERONET'][values]=np.mean(month_Data['AOD_AERONET'])
        
        y_data = data.groupby([data['Date_MODIS'].dt.year]).apply(helper)
        y_index = y_data.index.get_level_values(0).unique()
        
        y_end = pd.DataFrame(columns=y_index,index=['RMSE','R_deming','R_pearson','MAE','BIAS','MEAN_MODIS','MEAN_AERONET'])
        for values in y_index:
            year_Data = y_data.loc[values]
            if len(year_Data)==1:
                continue
            y_end.loc['RMSE'][values]=rmse(year_Data['AOD_MODIS'],year_Data['AOD_AERONET'])
            y_end.loc['R_deming'][values]=r_deming(year_Data['AOD_MODIS'],year_Data['AOD_AERONET'])
            y_end.loc['R_pearson'][values]=pearsonr(year_Data['AOD_MODIS'],year_Data['AOD_AERONET'])[0]
            y_end.loc['MAE'][values]=mae(year_Data['AOD_MODIS'],year_Data['AOD_AERONET'])
            y_end.loc['BIAS'][values]=bias(year_Data['AOD_MODIS'],year_Data['AOD_AERONET'])
            y_end.loc['MEAN_MODIS'][values]=np.mean(year_Data['AOD_MODIS'])
            y_end.loc['MEAN_AERONET'][values]=np.mean(year_Data['AOD_AERONET'])
        
        writer = pd.ExcelWriter('statistics_{}.xlsx'.format(_file[:-21]))
        general_data.to_excel(writer,'Estadistica_general')
        m_end.to_excel(writer,'Estadistica_mensual')
        y_end.to_excel(writer,'Estadistica_anual')
        writer.save()
    return general_data, m_end, y_end
    #Abro el archivo y guardo los datos en numpy.arrays (dtype=float)

#%%
if __name__ == '__main__':
    g_stats, m_stat, y_stat = main()