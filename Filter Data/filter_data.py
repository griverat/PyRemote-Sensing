# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 11:31:25 2017

@author: gerar
"""
#This script was made to filter data by location: South, North or Center
#It reads an ASCII with lat, lon and data columns
#It returns an ASCII of the same format with location headers

#%%
import os
import pandas as pd

#%%
class Filter_data(object):
    
    def __init__(self):
        self.name = "chl_situ.txt"
        self.bounds = {"norte":-8.5,"centro":-15,"sur":-20}
        
    def run(self):
        self.files_list = []
        for file in os.listdir(os.getcwd()):
            if file.endswith(self.name):
                self.files_list.append(file)
        return self.files_list
    
    def read_file(self,data_file):
        self.chl_data = pd.read_table(data_file, parse_dates=[0],infer_datetime_format = True)
        self.north = self.chl_data.loc[(self.chl_data["lat"] > self.bounds["norte"]) & (self.chl_data["lat"] < 0.)]
        self.center = self.chl_data.loc[(self.chl_data["lat"] > self.bounds["centro"]) & (self.chl_data["lat"] < self.bounds["norte"])]
        self.south = self.chl_data.loc[(self.chl_data["lat"] > self.bounds["sur"]) & (self.chl_data["lat"] < self.bounds["centro"])]
    
    def save_file(self):
        with open("chl_situ_filtrada.txt","w") as output:
            output.write("Norte\n")
        self.north.to_csv("chl_situ_filtrada.txt", index=None, sep="\t", mode="a")
        
        with open("chl_situ_filtrada.txt","a") as output:
            output.write("\nCentro\n")
        self.center.to_csv("chl_situ_filtrada.txt", index=None, sep="\t", mode="a")
        
        with open("chl_situ_filtrada.txt","a") as output:
            output.write("\nSur\n")
        self.south.to_csv("chl_situ_filtrada.txt", index=None, sep="\t", mode="a")
        
#%%
if __name__ == "__main__":
    run_filter = Filter_data()
    data = run_filter.run()[0]
    run_filter.read_file(data)
    run_filter.save_file()
