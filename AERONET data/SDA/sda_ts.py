# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 06:30:24 2017

@author: Gerardo A. Rivera Tello
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np
import os, datetime
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
    aeronet = pd.read_csv(filename, skiprows=4,index_col = False, na_values=['N/A'],
                          parse_dates={'times':[0,1]},
                          date_parser=dateparse,usecols=range(7))

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
def plot_series(pd_indata,station_name,ppath):
    fig, axes = plt.subplots(figsize=(9,4))
    aod_list = [headers for headers in list(pd_indata) if 'AOD' in headers]
    
    daily_values = pd.date_range('01-01-{}'.format(pd_indata.index.min().year),'31-12-{}'.format(pd_indata.index.min().year),freq='D')
    marker = itertools.cycle(('x', 'v', 's', 'o', '*')) 

    months = list(set(pd_indata.index.month))
    for value in months:
        to_plot = pd_indata.loc[pd_indata.index.month==value]
        
        for aod in aod_list:
            axes.plot(to_plot.index,pd_indata[aod],lw=0.8, marker = marker.next(),ms=3)
        
        filtered = daily_values[daily_values.month == to_plot.index.min().month]
        
        ##
        fig2, axes2 = plt.subplots(figsize=(9,4))
        axes2.plot(to_plot.index,pd_indata['FineModeFraction_500nm[eta]'],lw=0.8,marker='d',ms=3)
        axes2.set_ylim([0,1])
        axes2.set_xlim([filtered.min(),filtered.max()])
        axes2.set_yticks(np.arange(0,1.1,0.1))
        axes2.set_xticks(filtered)
        axes2.xaxis.set_major_locator(dates.DayLocator())
        axes2.xaxis.set_major_formatter(dates.DateFormatter('%d'))
        axes2.set_ylabel('SDA Fine Mode Fraction',fontsize=15)
        axes2.set_xlabel('Tiempo (dias)',fontsize=15)
        axes2.text(0.19,0.9\
                  ,'{} AERONET Data'.format(station_name)\
                  ,ha="center",va="center",fontsize=13\
                  ,bbox=dict(facecolor='none', edgecolor='black', boxstyle='round')\
                  ,transform=axes2.transAxes)
        axes2.legend(loc=0,numpoints=1,fontsize = 9,fancybox=True)
        fig2.savefig(os.path.join(ppath,"{}_finefrac.png".format(station_name)),dpi=500,bbox_inches='tight')
        ##
        
        axes.set_ylim([0,1.5])
        axes.set_xlim([filtered.min(),filtered.max()])
        
        axes.set_yticks(np.arange(0,1.6,0.1))
        axes.set_xticks(filtered)
        
        axes.set_ylabel('SDA Aerosol Optical Depth',fontsize=15)
        axes.set_xlabel('Tiempo (dias)',fontsize=15)
        
        axes.text(0.19,0.9\
                  ,'{} AERONET Data'.format(station_name)\
                  ,ha="center",va="center",fontsize=13\
                  ,bbox=dict(facecolor='none', edgecolor='black', boxstyle='round')\
                  ,transform=axes.transAxes)
    
        axes.xaxis.set_major_locator(dates.DayLocator())
        axes.xaxis.set_major_formatter(dates.DateFormatter('%d'))
        axes.legend(loc=0,numpoints=1,fontsize = 9,fancybox=True)
        fig.savefig(os.path.join(ppath,"{}_SDA.png".format(station_name)),dpi=500,bbox_inches='tight')

#%%
def single_plot(pd_indata,aod_list,date_limits,n,station_name,ppath):
    fig,axes = plt.subplots(figsize=(9,4))
    day_df = pd_indata.loc[(date_limits[n]<pd_indata.index)&(pd_indata.index<date_limits[n+1])]
    
    marker = itertools.cycle(('x', 'v', 's', 'o', '*')) 
    
    for aod in aod_list:
        axes.plot(day_df.index,day_df[aod],lw=0.8,marker = marker.next(),ms=2.7)
    
    hour_values = pd.date_range(day_df.index.min().date(),periods=24,freq='1h')
    
    ##
    fig2, axes2 = plt.subplots(figsize=(9,4))
    axes2.plot(day_df.index,day_df['FineModeFraction_500nm[eta]'],lw=0.8)
    axes2.set_ylim([0,1])
    axes2.set_xlim([hour_values.min(),hour_values.max()])
    axes2.set_yticks(np.arange(0,1.1,0.1))
    axes2.set_xticks(hour_values)
    axes2.xaxis.set_major_locator(dates.HourLocator())
    axes2.xaxis.set_major_formatter(dates.DateFormatter('%H'))
    axes2.set_ylabel('SDA Fine Mode Fraction',fontsize=15)
    axes2.set_xlabel('Tiempo (horas)',fontsize=15)
    axes2.legend(loc=0,numpoints=1,fontsize = 9,fancybox=True)
    axes2.text(0.15,0.79\
              ,day_df.index.min().date().strftime('%d/%m/%Y')\
              ,ha="center",va="center",fontsize=13\
              ,bbox=dict(facecolor='none', edgecolor='black', boxstyle='round')\
              ,transform=axes2.transAxes)
    axes2.text(0.19,0.9\
                  ,'{} AERONET Data'.format(station_name)\
                  ,ha="center",va="center",fontsize=13\
                  ,bbox=dict(facecolor='none', edgecolor='black', boxstyle='round')\
                  ,transform=axes2.transAxes)
    fig2.savefig(os.path.join(ppath,"{}_day{}_finefraction.png".format(station_name,day_df.index.min().day)),dpi=500,bbox_inches='tight')
    ##
    
    axes.set_ylim([0,1.5])
    axes.set_xlim([hour_values.min(),hour_values.max()])
    
    axes.set_yticks(np.arange(0,1.6,0.1))
    axes.set_xticks(hour_values)

    axes.set_ylabel('SDA Aerosol Optical Depth',fontsize=15)
    axes.set_xlabel('Tiempo (horas)',fontsize=15)
    
    axes.text(0.19,0.9\
              ,'{} AERONET Data'.format(station_name)\
              ,ha="center",va="center",fontsize=13\
              ,bbox=dict(facecolor='none', edgecolor='black', boxstyle='round')\
              ,transform=axes.transAxes)
    axes.text(0.15,0.79\
              ,day_df.index.min().date().strftime('%d/%m/%Y')\
              ,ha="center",va="center",fontsize=13\
              ,bbox=dict(facecolor='none', edgecolor='black', boxstyle='round')\
              ,transform=axes.transAxes)

    axes.xaxis.set_major_locator(dates.HourLocator())
    axes.xaxis.set_major_formatter(dates.DateFormatter('%H'))
    axes.legend(loc=0,numpoints=1,fontsize = 9,fancybox=True)
    fig.savefig(os.path.join(ppath,"{}_day{}_SDA.png".format(station_name,day_df.index.min().day)),dpi=500,bbox_inches='tight')

#%%
def day_plot(pd_indata,station_name,directory):
    aod_list = [headers for headers in list(pd_indata) if 'AOD' in headers]
    diff = datetime.timedelta(days=1)
    date_limits = pd.date_range(pd_indata.index.min().date(),pd_indata.index.max().date()+diff,freq='D')
    for n in range(len(date_limits)-1):
        single_plot(pd_indata,aod_list,date_limits,n,station_name,directory)
        print "Dia {} listo".format(n+1)
    
#%%
if __name__ == '__main__':
    for files in os.listdir(os.getcwd()):
        if files.endswith('.ONEILL_15'):
            df = read_aeronet(files)
            name = files.split('_')
            plot_dir = os.path.join(os.getcwd(),'{}_SDAplots'.format(name[2].split('.')[0]))
            if not os.path.exists(plot_dir):
                os.mkdir(plot_dir)
            plot_series(df,name[2].split('.')[0],plot_dir)
            day_plot(df,name[2].split('.')[0],plot_dir)
