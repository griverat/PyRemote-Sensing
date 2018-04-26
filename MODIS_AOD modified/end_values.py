# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 15:47:38 2018

@author: gerar
"""
import os
import pandas as pd
import numpy as np

#%%
def read_table(dataframe):
    data = pd.read_table(dataframe)
    data['Difference']=np.abs(data['AOD_AERONET']-data['AOD_MODIS'])
    drop_data = data.dropna()
    dup = list(drop_data[drop_data.duplicated(subset='Date_MODIS')]['Date_MODIS'])
    for date in dup:
        dummy = drop_data[drop_data['Date_MODIS']==date]
        stay = dummy.loc[(dummy['Difference']==dummy['Difference'].min())].index
        drop_data = drop_data.drop(dummy.index.drop(stay))
    del drop_data['Difference']
    return drop_data
        

#%%
if __name__ == '__main__':
    matched_files = [x for x in os.listdir(os.getcwd()) if x.endswith('_matched_data.txt')]
    for files in matched_files:
        end_val = read_table(files)
        end_val.to_csv('{}_end.txt'.format(files[:-4]), index=None, sep='\t')