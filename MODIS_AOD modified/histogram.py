# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 13:08:16 2018

@author: gerar
"""

import os, datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates

#%%
def get_data(dataframe):
    data = pd.read_table(dataframe,usecols=[0])
    data['Date_MODIS'] = data['Date_MODIS'].astype('datetime64')
    
    mdata = data.groupby([data['Date_MODIS'].dt.year,data['Date_MODIS'].dt.month]).count()
#    freq.index = pd.MultiIndex.from_tuples([(x[0],calendar.month_abbr[x[1]]) for x in freq.index])
    mdata.index.rename(['Year','Month'],inplace=True)
    mdata.reset_index(inplace=True)
    mdata.index=mdata.apply(lambda x:datetime.datetime.strptime("{0} {1} 00:00:00".format(x['Year'],x['Month']), "%Y %m %H:%M:%S"),axis=1)
    del mdata['Year'], mdata['Month']
    
    yearly = data.groupby([data['Date_MODIS'].dt.year]).count()
    yearly.index.rename('Year',inplace=True)
    yearly.reset_index(inplace=True)
    yearly.index=yearly.apply(lambda x:datetime.datetime.strptime('{0} 01 00:00:00'.format(x['Year']),'%Y %m %H:%M:%S'),axis=1)
    del yearly['Year']
    
    monthly = data.groupby([data['Date_MODIS'].dt.month]).count()
    monthly.index.rename('Month',inplace=True)
    monthly.reset_index(inplace=True)
    monthly.index=monthly.apply(lambda x:datetime.datetime.strptime('2018 {0} 00:00:00'.format(x['Month']),'%Y %m %H:%M:%S'), axis=1)
    
    return mdata, monthly, yearly

def data_hist(dataframe):
    fig, ax = plt.subplots(figsize=(25,7))
    ax.bar(dataframe.index,dataframe['Date_MODIS'],width=25)
    
#    freq.plot(kind='bar', ax=ax)
#    ax.set_xticklabels(freq.index.strftime('%Y-%m'))
#    ax.set_xticks(pd.date_range(freq.index.min(),freq.index.max(),freq='MS'))
    ax.xaxis.set_minor_locator(dates.MonthLocator())
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    
    ax.xaxis.set_major_locator(dates.YearLocator())
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y'))
    
    ax.tick_params(axis='x',which='minor',labelsize=5)
    
    ax.xaxis.set_tick_params(which='major', pad=15)
    
    fig.tight_layout()
#    fig.savefig("data_freq.png",dpi=800,bbox_inches='tight')  

#%%
def yearly_hist(dataframe):
    fig, ax = plt.subplots(figsize=(15,7))
    ax.bar(dataframe.index,dataframe['Date_MODIS'],width=200)
    
#    freq.plot(kind='bar', ax=ax)
#    ax.set_xticklabels(freq.index.strftime('%Y-%m'))
#    ax.set_xticks(pd.date_range(freq.index.min(),freq.index.max(),freq='MS'))
#    ax.xaxis.set_minor_locator(dates.MonthLocator())
#    ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    
    ax.xaxis.set_major_locator(dates.YearLocator())
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y'))
    
#    ax.tick_params(axis='x',which='minor',labelsize=5)
    
#    ax.xaxis.set_tick_params(which='major', pad=15)
    
    fig.tight_layout()
#    fig.savefig("yearly_freq.png",dpi=800,bbox_inches='tight')

#%%
def monthly_hist(dataframe):
    fig, ax = plt.subplots(figsize=(15,7))
    ax.bar(dataframe.index,dataframe['Date_MODIS'],width=20)
    
#    freq.plot(kind='bar', ax=ax)
#    ax.set_xticklabels(freq.index.strftime('%Y-%m'))
#    ax.set_xticks(pd.date_range(freq.index.min(),freq.index.max(),freq='MS'))
#    ax.xaxis.set_minor_locator(dates.MonthLocator())
#    ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    
    ax.xaxis.set_major_locator(dates.MonthLocator())
    ax.xaxis.set_major_formatter(dates.DateFormatter('%b'))
    
#    ax.tick_params(axis='x',which='minor',labelsize=5)
    
#    ax.xaxis.set_tick_params(which='major', pad=15)
    
    fig.tight_layout()
#    fig.savefig("monthly_freq.png",dpi=800,bbox_inches='tight')
    
#%%
if __name__ == '__main__':
    files = [x for x in os.listdir(os.getcwd()) if x.endswith('_end.txt')]
    mdata,month, year = get_data(files[0])
    data_hist(mdata)
    monthly_hist(month)
    yearly_hist(year)