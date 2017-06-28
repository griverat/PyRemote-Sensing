# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 06:30:24 2017

@author: Rolando Renee Badaracco Meza
"""

import pandas as pd
import os

#function from http://blog.rtwilson.com/reading-aeronet-data-in-pandas-a-simple-helper-function/
def read_aeronet(filename): 
    """Read a given AERONET AOT data file, and return it as a dataframe.
    
    This returns a DataFrame containing the AERONET data, with the index
    set to the timestamp of the AERONET observations. Rows or columns
    consisting entirely of missing data are removed. All other columns
    are left as-is.
    """
    dateparse = lambda x: pd.datetime.strptime(x, "%d:%m:%Y %H:%M:%S")
    aeronet = pd.read_csv(filename, skiprows=4, na_values=['N/A'],
                          parse_dates={'times':[0,1]},
                          date_parser=dateparse)

    aeronet = aeronet.set_index('times')
    del aeronet['Julian_Day']
    
    # Drop any rows that are all NaN and any cols that are all NaN
    # & then sort by the index
    an = (aeronet.dropna(axis=1, how='all')
                .dropna(axis=0, how='all')
                .rename(columns={'Last_Processing_Date(dd/mm/yyyy)': 'Last_Processing_Date'})
                .sort_index())

    return an

if __name__ == '__main__':
    for files in os.listdir(os.getcwd()):
        if files.endswith('.lev20'):
            df = read_aeronet(files)
            df['AOT_550']=df['AOT_500']*(0.55/0.5)**(-df['440-675Angstrom'])
            new_df = df[['AOT_550']].copy()
            new_df.index.names=['DATE TIME']
            new_df.to_csv("aeronet_data.txt",sep='\t')