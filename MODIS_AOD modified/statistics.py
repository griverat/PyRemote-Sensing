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
def db_results(row_names,data):
    ix_names=['RMSE','R_deming','R_pearson','MAE','BIAS','MEAN_MODIS','MEAN_AERONET']
    if len(row_names) == 1:
        db = pd.DataFrame(columns=row_names,index=ix_names)
        db.loc['RMSE']=rmse(data[0],data[1])
        db.loc['R_deming']=r_deming(data[0],data[1])
        db.loc['R_pearson']=pearsonr(data[0],data[1])[0]
        db.loc['MAE']=mae(data[0],data[1])
        db.loc['BIAS']=bias(data[0],data[1])
        db.loc['MEAN_data[0]']=np.mean(data[0])
        db.loc['MEAN_data[1]']=np.mean(data[1])
    else:
        db = pd.DataFrame(columns=range(1,13),index=ix_names)
        for col in row_names:
            t_data = data.loc[col]
            if len(t_data) <= 2:
                continue
            db.loc['RMSE'][col]=rmse(t_data['AOD_MODIS'],t_data['AOD_AERONET'])
            db.loc['R_deming'][col]=r_deming(t_data['AOD_MODIS'],t_data['AOD_AERONET'])
            db.loc['R_pearson'][col]=pearsonr(t_data['AOD_MODIS'],t_data['AOD_AERONET'])[0]
            db.loc['MAE'][col]=mae(t_data['AOD_MODIS'],t_data['AOD_AERONET'])
            db.loc['BIAS'][col]=bias(t_data['AOD_MODIS'],t_data['AOD_AERONET'])
            db.loc['MEAN_MODIS'][col]=np.mean(t_data['AOD_MODIS'])
            db.loc['MEAN_AERONET'][col]=np.mean(t_data['AOD_AERONET'])
    
    return db

#%%
def main():
    files = [x for x in os.listdir(os.getcwd()) if x.endswith("matched_data_end.txt")]
    
    for _file in files:
        modis, aeronet = get_data(_file)
        
        general_data = db_results(['Statistics'],[modis,aeronet])
        
        data = pd.read_table(_file,usecols=[0,2,4])
        data['Date_MODIS'] = data['Date_MODIS'].astype('datetime64[ns]')
        
        m_data = data.groupby([data['Date_MODIS'].dt.month]).apply(helper)
        m_index = m_data.index.get_level_values(0).unique()
        m_end = db_results(m_index,m_data)
        
        y_data = data.groupby([data['Date_MODIS'].dt.year]).apply(helper)
        y_index = y_data.index.get_level_values(0).unique()
        y_end = db_results(y_index,y_data)
        
        writer = pd.ExcelWriter('statistics_{}.xlsx'.format(_file[:-21]))
        general_data.to_excel(writer,'Estadistica_general')
        m_end.to_excel(writer,'Estadistica_mensual')
        y_end.to_excel(writer,'Estadistica_anual')
        writer.save()
    return general_data, m_end, y_end

#%%
if __name__ == '__main__':
    g_stats, m_stat, y_stat = main()