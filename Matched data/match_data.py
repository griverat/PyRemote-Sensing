# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 17:36:50 2017

@author: gerar
"""

#%%
#Importo las librerias:
#   1. os : que me ayudara a buscar los archivos en el directorio
#   2. numpy: crea arreglos con manejo numerico sencillo
#   3. pandas: para el manejo de dataframes con timestamps
import os
import numpy as np
import pandas as pd

#%%

class Match_Data(object):
    
    def run(self):
        self.files_list = []
        for files in os.listdir(os.getcwd()):
            if files.endswith(".txt"):
                self.files_list.append(files)
        return self.files_list
        
    def read_files(self, modis_file,aeronet_file):
        #MODIS
        self.modis_data = pd.read_table(modis_file, header = None, parse_dates = [[0,1]], usecols=[0,1])
        self.modis_end = pd.read_table(modis_file, header = None)
        #Agrego un header a mi dataframe
        self.modis_data.columns = ["Date_MODIS Time_MODIS"]
        self.modis_end.columns = ["Date_MODIS", "Time_MODIS", "AOD_MODIS"]
        
        #AERONET
        self.aeronet_data = pd.read_table(aeronet_file, header = None, parse_dates = [[0,1]], usecols=[0,1])
        self.aeronet_end = pd.read_table(aeronet_file, header = None, usecols=[1,2])
        self.aeronet_data.columns = ["Date_AERONET Time_AERONET"]
        self.aeronet_end.columns=["Time_AERONET", "AOD_AERONET"]
        print "Archivos Leidos.\nProcesando..."

    #Defino la funcion que encontrara los vaores cercanos a la fecha y hora MODIS
    def find_closest_date(self, timepoint, time_series):
        # Tomo de entrada una pd.Timestamp() y una pd.Series con fechas
        # calculo el delta entre `timepoint` y cada fecha en`time_series`
        # devuelvo la fecha con hora más cercana junto al valor del AOD_AERONET
        deltas = np.abs(time_series - timepoint)
        #Calculo los indices en donde la diferencia de tiempos es a lo mucho
        #+-30 min
        passer = np.where(deltas < pd.Timedelta("00:30:59"))
        #Compruebo si existen coincidencias para guardar los valores
        if len(passer[0]) != 0:
            idx_closest_date = np.argmin(deltas[passer[0]])
            #Diccionario que contenerá los valores cercanos al dato de entrada
            res={"closest_time":self.aeronet_end["Time_AERONET"].ix[idx_closest_date], "aod_value": self.aeronet_end["AOD_AERONET"].ix[idx_closest_date]}
            #indices del diccionario para ser introducidos en pd.Series
            idx = ['closest_time', 'aod_value']
            return pd.Series(res, index=idx)
        #En caso de no haber la fecha MODIS en la base de datos AERONET
        #lleno los valosre con NaT(Not a Time) y NaN(Not a Number)
        elif len(passer[0]) == 0:
            res = {"closest_time": "NaN","aod_value": "NaN"}
            idx = ['closest_time', 'aod_value']
            return pd.Series(res, index=idx)
    
    def match_aod(self,modis_grid,station_name):
        self.modis_end[['Time_AERONET', 'AOD_AERONET']] = self.modis_data["Date_MODIS Time_MODIS"].apply(self.find_closest_date,args=[self.aeronet_data["Date_AERONET Time_AERONET"]])
        self.modis_end.to_csv("{}{}_matched_data.txt".format(station_name,modis_grid),index =None, sep="\t")

#%%

if __name__ == "__main__":
    run_match = Match_Data()
    files = run_match.run()
    modis_files=[]
    for name in files:
        if name.endswith("MODIS.txt"):
            modis_files.append(name)
        elif name.endswith("AERONET.txt"):
            aeronet_file = name
    for modis_grid in modis_files:
        run_match.read_files(modis_grid,aeronet_file)
        run_match.match_aod(modis_grid[-13:-10],aeronet_file[:-12])