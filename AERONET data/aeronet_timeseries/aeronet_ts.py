# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 06:30:24 2017

@author: Rolando Renee Badaracco Meza
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
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

def plot_series(pd_indata):
    fig, axes = plt.subplots(figsize=(12,3))
    aot_list = [headers for headers in list(pd_indata) if 'AOT' in headers]
    for aot in aot_list:
        axes.plot(pd_indata.index,pd_indata[aot])
    
#    axes.set_xlim([pd_indata.index.min(),pd_indata.index.max()])
    axes.set_ylim([0,1.5])

    axes.xaxis.set_minor_locator(dates.DayLocator())
    axes.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
    axes.xaxis.set_major_locator(dates.MonthLocator())
    axes.xaxis.set_major_formatter(dates.DateFormatter('\n%b\n%Y'))
    axes.legend(loc=0,numpoints=1,fontsize = 9,fancybox=True)
#    fig.autofmt_xdate()

if __name__ == '__main__':
    for files in os.listdir(os.getcwd()):
        if files.endswith('.lev15'):
            df = read_aeronet(files)
            plot_series(df)
#            df['AOT_550']=df['AOT_500']*(0.55/0.5)**(-df['440-675Angstrom'])
#            new_df = df[['AOT_550']].copy()
#            new_df.index.names=['DATE TIME']
#            new_df.to_csv("aeronet_data.txt",sep='\t')