# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 06:30:24 2017

@author: Gerardo A. Rivera Tello
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os, datetime, matplotlib
import itertools
#%%
#function from http://blog.rtwilson.com/reading-aeronet-data-in-pandas-a-simple-helper-function/
def read_aeronet(filename): 
    """Read a given AERONET AOT data file, and return it as a dataframe.
    
    This returns a DataFrame containing the AERONET data, with the index
    set to the timestamp of the AERONET observations. Rows or columns
    consisting entirely of missing data are removed. All other columns
    are left as-is.
    """
    dateparse = lambda x: pd.datetime.strptime(x, "%d:%m:%Y %H:%M:%S")
    aeronet = pd.read_csv(filename, skiprows=3, na_values=['N/A'],
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


#%%
def single_plot(pd_indata,dates_list,date_limits,n,station_name,ppath):
    fig,axes = plt.subplots(figsize=(9,4))
    day_df = pd_indata.loc[(date_limits[n]<pd_indata.index)&(pd_indata.index<date_limits[n+1])]
    dates_list = day_df.index
    day_df = day_df.transpose()
    day_df = day_df.drop(day_df.index[range(22,54)])
    
    marker = itertools.cycle(('x', 'v', 's', 'o', '*')) 
    
    for values in dates_list:
        axes.plot(day_df.index,day_df[values],lw=0.8,marker = marker.next(),ms=2.7)
    
    axes.set_ylim([0,0.14])
    
    axes.set_yticks(np.arange(0,0.15,0.01))
    axes.set_xscale('log')
    axes.set_xticks([0.01,0.1,1,10,100])

    axes.set_ylabel('dV(r)/dln(r)',fontsize=15)
    axes.set_xlabel('Radio (r)',fontsize=15)
    
    axes.text(0.19,0.9\
              ,'{} AERONET Data'.format(station_name)\
              ,ha="center",va="center",fontsize=13\
              ,bbox=dict(facecolor='none', edgecolor='black', boxstyle='round')\
              ,transform=axes.transAxes)

    axes.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    axes.legend(loc=0,numpoints=1,fontsize = 9,fancybox=True)
    fig.savefig(os.path.join(ppath,"{}_day{}_partsize.png".format(station_name,dates_list.min().day)),dpi=500,bbox_inches='tight')
    fig.clf()

#%%
def day_plot(pd_indata,station_name,directory):
    dates_list = pd_indata.index
    diff = datetime.timedelta(days=1)
    date_limits = pd.date_range(pd_indata.index.min().date(),pd_indata.index.max().date()+diff,freq='D')
    for n in range(len(date_limits)-1):
        single_plot(pd_indata,dates_list,date_limits,n,station_name,directory)
        print "Dia {} listo".format(n+1)
    
#%%
if __name__ == '__main__':
    for files in os.listdir(os.getcwd()):
        if files.endswith('.siz'):
            df = read_aeronet(files)
            name = files.split('_')
            plot_dir = os.path.join(os.getcwd(),'{}_PARTSplots'.format(name[2].split('.')[0]))
            if not os.path.exists(plot_dir):
                os.mkdir(plot_dir)
            day_plot(df,name[2].split('.')[0],plot_dir)
