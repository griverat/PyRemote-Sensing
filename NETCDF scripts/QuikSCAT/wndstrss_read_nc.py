#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 10 15:23:19 2017

@author: DangoMelon0701
"""
from scipy.io import netcdf
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

#%%
def plot_data(data,cbar=0,save_img=0,name='image'):
    norm = mpl.colors.Normalize(vmin=-0.5, vmax=0.5)
    cmap = mpl.cm.get_cmap('jet')
    plot,axs = plt.subplots()
    raw_data = axs.imshow(data,interpolation="gaussian",cmap=cmap,norm=norm)
    if cbar == 1:
        cbar = plot.colorbar(raw_data)
    if save_img == 1:
        plt.savefig("{}.png".format(name),dpi=1000,bbox_inches='tight')

#%%
def rmse(predictions, targets):
    return np.sqrt(np.nanmean((predictions - targets) ** 2))
#%%

list_files = []
drag_c = 1e-3
air_ro = 1.2
for files in os.listdir(os.getcwd()):
    if files.endswith('.nc'):
        list_files.append(files)

for nc_files in list_files:
    open_file = netcdf.NetCDFFile(nc_files,'r')
    
    #Velocidad zonal
    znl_wnd_speed = open_file.variables['zonal_wind_speed']
    np_znl_speed = znl_wnd_speed[:]*znl_wnd_speed.scale_factor
    np_znl_speed[np.where(np_znl_speed==np_znl_speed.max())]=np.nan
    #Velocidad meridional
    mrdnl_wnd_speed = open_file.variables['meridional_wind_speed']
    np_mrdnl_speed = mrdnl_wnd_speed[:]*mrdnl_wnd_speed.scale_factor
    np_mrdnl_speed[np.where(np_mrdnl_speed==np_mrdnl_speed.max())]=np.nan
    #Magnitud del vector velocidad
    np_wnd_module = np.sqrt(np.power(np_znl_speed,2)+np.power(np_mrdnl_speed,2))
    #Calculo de estres
    tao_x = air_ro*drag_c*np_znl_speed*np_wnd_module
    tao_y = air_ro*drag_c*np_mrdnl_speed*np_wnd_module    
    
    #Leo los datos de estres para comparar
    znl_wnd_stress = open_file.variables['zonal_wind_stress']
    np_znl_stress = znl_wnd_stress[:]*znl_wnd_stress.scale_factor
    np_znl_stress[np.where(np_znl_stress==np_znl_stress.max())]=np.nan
    np_znl_stress[np.where(np_znl_stress==np.nanmax(np_znl_stress))]=np.nan
    np_znl_stress[np.where(np_znl_stress==np.nanmin(np_znl_stress))]=np.nan
    
    mrdnl_wnd_stress = open_file.variables['meridional_wind_stress']
    np_mrdnl_stress = mrdnl_wnd_stress[:]*mrdnl_wnd_stress.scale_factor
    np_mrdnl_stress[np.where(np_mrdnl_stress==np_mrdnl_stress.max())]=np.nan
    np_mrdnl_stress[np.where(np_mrdnl_stress==np.nanmax(np_mrdnl_stress))]=np.nan
    np_mrdnl_stress[np.where(np_mrdnl_stress==np.nanmin(np_mrdnl_stress))]=np.nan
    
    open_file.close()
#%%
    #Grafica de dispersión para comparar la data
    x_limit = 0.45
    y_limit = 0.45
    fig, axes = plt.subplots(figsize=(7,7))
    #linea 1:1
    _11line = np.linspace(0,x_limit,2)
    axes.plot(_11line,_11line, color ='black',lw=0.6)
    #scatter plot
    axes.scatter(np_mrdnl_stress,tao_y,edgecolors="black",linewidth=0.1,s=10)
    axes.axis([0,x_limit,0,y_limit],fontsize=10)
    #nombre de los ejes y grafico
    fig.suptitle('QuikSCAT {}'.format(nc_files),fontsize=16)
    axes.set_ylabel('Computed Meridional Wind Stress',fontsize=16)
    axes.set_xlabel('QuikSCAT Meridional Wind Stress',fontsize=16)
    #valores adicionales
    rmse_value = rmse(np_mrdnl_stress,tao_y)
    axes.text(0.08,0.78,"(RMSE={:.3f})".format(rmse_value),fontsize=13.5,\
          transform=axes.transAxes)
    axes.grid(linestyle='--')
    #guardando la figura
    fig.savefig("mrdstrss_scatter_plot.png",dpi=1000,bbox_inches='tight')
#%%
    plot_data(tao_x,1,1,'zonal_strees_calculated')
    plot_data(np_znl_stress,1,1,'zonal_stress_given')
    plot_data(tao_y,1,1,'meridional_strees_calculated')
    plot_data(np_mrdnl_stress,1,1,'meridional_stress_given')
#%%
    break
