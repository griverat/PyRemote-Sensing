# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 13:17:45 2016

@author: gerar
"""
# Este archivo toma como datos de entrada un ASCII 
# con 5 Columnas
# Date_MODIS	Time_MODIS	AOD_MODIS	Time_AERONET	AOD_AERONET
# Se puede usar en conjunto con el codigo llamado
# pd_match_data.py
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
#from datetime import timedelta as delt
#from scipy.stats.stats import pearsonr

#%%
#Defino los valores máximos de los ejes en el plot
x_limit = 0.9
y_limit = 0.9

#%%
#Datos de la estacion|
AERONET_station = "Rio Branco"
years_range="2015-2016"
x_label = r"AERONET Level 2.0 AOD $\mu m$"
y_label = "MODIS AQUA AOD at 10km"

#%%
#Cantidad de pixeles a tomar en promedio
grid = "3x3"
#%%
#Defino la fuente estilo LaTeX
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

#%%
#Defino la funcion para rmse
def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())
    
#%%
#Encuentro el archivo en formato txt a plottear
file_to_plot = [x for x in os.listdir(os.getcwd()) \
               if x.endswith("{}{}_matched_data.txt".format(\
                             AERONET_station.lower().replace(" ",""),grid))]
#Abro el archivo y guardo los datos en numpy.arrays (dtype=float)
modis_data,aeronet_data = np.loadtxt(file_to_plot[0],skiprows = 1,usecols=(2,4),unpack=True)

#Leo la data para graficar una serie de tiempo
data = pd.read_table(file_to_plot[0], parse_dates=[0],infer_datetime_format = True,usecols=(0,2,4)) #, parse_dates=[0],infer_datetime_format = True
data = data.dropna() #[pd.notnull(data['AOD_AERONET'])]
data = data.set_index('Date_MODIS')

print "Archivo Leido\nProcesando ..."
np.seterr(all='ignore')
#%%
#Realizo los calculos del EE
_ee = np.abs(0.05 + 0.15*aeronet_data)
ee_plus = aeronet_data + _ee
ee_minus = aeronet_data - _ee

#1- Dentro del EE:
within_ee = modis_data[np.logical_and(ee_minus<modis_data,modis_data<ee_plus)]
xwithin_ee = aeronet_data[np.logical_and(ee_minus<modis_data,modis_data<ee_plus)]

#2- Por encima del EE:
above_ee = modis_data[ee_plus<modis_data]
xabove_ee = aeronet_data[ee_plus<modis_data]

#3- Por debajo del EE:
below_ee = modis_data[modis_data<ee_minus]
xbelow_ee = aeronet_data[modis_data<ee_minus]

#--Total de Puntos--
n_tot=len(above_ee)+len(within_ee)+len(below_ee)
#%%
#Calculo los parametros de las rectas EE+ y EE-
idx = np.isfinite(aeronet_data) 
m_plus,b_plus = np.polyfit(aeronet_data[idx],ee_plus[idx],1)
m_minus,b_minus = np.polyfit(aeronet_data[idx],ee_minus[idx],1)

#%%
#Calculo del R del grafio
#r_coef = pearsonr(aeronet_data[idx],modis_data[idx])

#Calculo del RMSE
rmse_value = rmse(modis_data[idx],aeronet_data[idx])
#%%
#Calculo la FOE para otra grafica
FOE = (modis_data-aeronet_data) / _ee
FOE = FOE[np.isfinite(FOE)]
data['FOE']=FOE
data = data.sort_index()
#%%
print "Realizando la grafica...\n"
#Puntos para graficar la linea 1:1
_11line = np.linspace(0,x_limit,2)

#Realizamos el scatter plot del pd.dataframe
fig, axes = plt.subplots(figsize=(7,7))
#axes.scatter(aeronet_data,modis_data)

#Plottear la data: above EE, within EE y below EE
axes.scatter(xabove_ee,above_ee,edgecolors="black",linewidth=1,s=10,c="blue",label="%\tAbove EE\t=\t{:.2%}".format(float(len(above_ee))/n_tot))
axes.scatter(xwithin_ee,within_ee,edgecolors="black",linewidth=1,s=10,c="red",label="%\tWithin EE\t=\t{:.2%}".format(float(len(within_ee))/n_tot))
axes.scatter(xbelow_ee,below_ee,edgecolors="black",linewidth=1,s=10,c="green",label="%\tBelow EE\t=\t{:.2%}".format(float(len(below_ee))/n_tot))

#Inserto la leyenda del plot
axes.legend(loc=2,scatterpoints=1,labelspacing=0.7,fontsize=13.5,handlelength=0.6,frameon=False)

#Dibujo las lineas 1:1, EE+ y EE-
axes.plot(_11line,_11line, color ='black',lw=0.6)
axes.plot(_11line,m_plus*_11line+b_plus,color = 'black', ls='--')
axes.plot(_11line,m_minus*_11line+b_minus,color = 'black', ls='--')

#Nombre de los ejes
axes.set_ylabel(y_label,fontsize=19)
axes.set_xlabel(x_label,fontsize=19)

#Nombre de la estación con el rango de años
axes.text(0.75,0.2,"({})\n\n({})".format(AERONET_station,years_range),\
          ha="center",va="center",fontsize=17,transform=axes.transAxes)
#axes.text(0.08,0.78,"(R={:.3f}, RMSE={:.3f})".format(r_coef[0],rmse_value),fontsize=13.5,\
#          transform=axes.transAxes)
axes.text(0.08,0.76,"(N={})".format(n_tot),fontsize=13.5,\
          transform=axes.transAxes)

#Limites del grafico con grillas
axes.axis([0,x_limit,0,y_limit],fontsize=10)
axes.tick_params(labelsize=13)
axes.grid(linestyle='--')



print "Guardando las imagenes en el directorio actual"
##Guardo el archivo en jpeg
fig.savefig("{}_AOD.jpeg".format(AERONET_station),dpi=1000,bbox_inches='tight')
print "\nScatter Plot Guardado"

##%%
##Obtengo las fechas
#dates = data.index.to_pydatetime()
#
##Grafico la serie de tiempo
#fig2, axes2 = plt.subplots(figsize=(8,3))
#
##Limites del eje y con saltos a mostrar
#axes2.set_ylim([-2.5,2.5])
##axes2.set_xlim([data.index.to_pydatetime().min(),data.index.to_pydatetime().max()])
#major_yticks=np.arange(-2.5,3,0.5)
#axes2.set_yticks(major_yticks)
#
##Linea horizontal
#t_delta = delt(20)
#axes2.hlines([1,0,-1],xmin=dates.min()-t_delta,xmax=dates.max()+t_delta,linestyle='dotted')
#
##Datos
#axes2.plot(dates,data['FOE'],'v-',linewidth='0',label='MYD04_L2 AOD')
#axes2.legend(loc=9,numpoints=1,fontsize = 9,fancybox=True)
#
##Nombre de los ejes
##axes2.set_xlabel("Fecha",fontsize=12)
#axes2.set_ylabel("Fraccion del Error Esperado (FOE)",fontsize=12)
#axes2.set_title("{} {}".format(AERONET_station,years_range))
#
#fig2.autofmt_xdate()
#
#
#
#plt.show()
###Guardo el archivo en jpeg
#fig2.savefig("{}_FOE.jpeg".format(AERONET_station),dpi=1000)
#print "\nFOE guardado"
#print "Proceso Terminado\n"
##os.system("pause")
