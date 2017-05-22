# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 11:56:01 2017

@author: gerar
"""

import os
#os.environ['GDAL_PATH'] = r'C:/Users/gerar/Anaconda2/pkgs/libgdal-2.1.0-vc9_0/Library/share/gdal'
import gdal
import numpy as np

#%%
#Class to read ASTER hdf
class ReadAster(object):
    
    def __init__(self):
        self.template = "HDF4_EOS:EOS_SWATH:{}:TIR_Swath:ImageData{}"
        
        # Create UTM zone code numbers    
        self.utm_n = [i+32600 for i in range(60)]
        self.utm_s = [i+32700 for i in range(60)]
        
        #Constants
        self.c1=1.19104356e-16
        self.c2=1.43876869e-2
        self.efwl = {10:8.291e-6,11:8.634e-6,12:9.075e-6,13:10.657e-6,14:11.318e-6}
                                                    
    def radiometric_calibration(self,UCC,DN):
        self.radiance = UCC*(DN-1.)
        self.radiance[self.radiance<0]=0
        return self.radiance
        
    def gdal_open(self,file_name,band_number=None):
        if band_number != None:
            self.band = gdal.Open(self.template.format(file_name,band_number),gdal.GA_ReadOnly)
            
            #Fetch Metadata
            self.meta = self.band.GetMetadata()        
    
            #Get the digital numbers values in an array:
            self.dn = self.band.ReadAsArray()
    
            #Get the UCC for the band:
            self.UCC = float(self.meta["INCL{}".format(band_number)])
            
            #Get the radiance
            self.rad = self.radiometric_calibration(self.UCC,self.dn)
            
        else:
            self.band = gdal.Open(file_name,gdal.GA_ReadOnly)
            return self.band.ReadAsArray()
        
    def calc_tbright(self, band_number):
        self.argument = (self.c1/((self.efwl[band_number]**5)*self.rad*1000000))+1.
        self.tbright = self.c2/(self.efwl[band_number]*np.log(self.argument))
        return self.tbright
    
    def georef(self):
        # Define UL, LR, UTM zone    
        self.ul = [np.float(x) for x in self.meta['UPPERLEFTM'].split(', ')]
        self.lr = [np.float(x) for x in self.meta['LOWERRIGHTM'].split(', ')]
        self.utm = np.int(self.meta['UTMZONENUMBER'])
        self.n_s = np.float(self.meta['NORTHBOUNDINGCOORDINATE'])
        
        # Define UTM zone based on North or South
        if self.n_s < 0:
            self.utm_zone = self.utm_s[self.utm]
            ul_y = self.ul[0] + 10000000
            ul_x = self.ul[1]
        
            lr_y = self.lr[0] + 10000000
            lr_x = self.lr[1]
        else:
            self.utm_zone = self.utm_n[self.utm]
            ul_y = self.ul[0] 
            ul_x = self.ul[1]
        
            lr_y = self.lr[0] 
            lr_x = self.lr[1]
        
        self.y_res = -1 * round((max(ul_y, lr_y)-min(ul_y, lr_y))/self.band.RasterYSize)
        self.x_res = round((max(ul_x, lr_x)-min(ul_x, lr_x))/self.band.RasterXSize)
        
        # Define UL x and y coordinates based on spatial resolution           
        self.ul_yy = ul_y - (self.y_res/2)
        self.ul_xx = ul_x - (self.x_res/2)
  
    def save_aster(self,filename,dataset,file_desc,band_number=None):
        # Define output GeoTiff CRS and extent properties
        if band_number != None:
            self.out_ds = gdal.GetDriverByName("GTiff").Create("{}_{}_{}.tif".format(filename,file_desc,band_number),self.band.RasterXSize,self.band.RasterYSize,1,gdal.GDT_Float32)
        else:
            self.out_ds = gdal.GetDriverByName("GTiff").Create("{}_{}.tif".format(filename,file_desc),self.band.RasterXSize,self.band.RasterYSize,1,gdal.GDT_Float32)
        
        if self.band.GetProjection() == "":
            self.georef()
            srs = gdal.osr.SpatialReference()
            srs.ImportFromEPSG(self.utm_zone)
            self.out_ds.SetProjection(srs.ExportToWkt())
            self.out_ds.SetGeoTransform((self.ul_xx, self.x_res, 0., self.ul_yy, 0., self.y_res))
        else:
            self.out_ds.SetProjection(self.band.GetProjection())
            self.out_ds.SetGeoTransform(self.band.GetGeoTransform())

        self.out_band = self.out_ds.GetRasterBand(1)
        self.out_band.WriteArray(dataset)
        del self.out_ds, self.band, self.out_band
        print "Archivo escrito en el disco"
    
    def get_tbright(self,name):
        tbright_files = []
        for files in os.listdir(os.getcwd()):
            if name+"_tbright" in files:
                tbright_files.append(files)
        return tbright_files
    
    def calc_sst(self,band_10,band_11,band_12,band_13,band_14):
        return 0.814963-0.241580*band_10+0.364233*band_11+0.869658*band_12+0.207910*band_13-0.105355*band_14-273.768

    def calc_sst2(self,band_13,band_14):
        return 0.999314*band_13+2.30195*(band_13-band_14)-273.768
        
    def run(self):
        files_list = []
        try:
            for files in os.listdir(os.getcwd()):
                if files.endswith(".hdf"):
                    files_list.append(files)
            return files_list
        #Error a mostrar en caso no encuentre archivos con la extension
        except:
            print('No se encontro archivos con la extensión .hdf en el diretorio de trabajo')

#%%
#Secuencia a correr en caso de no importar   
if __name__ == "__main__":
    calc = ReadAster()
    files = calc.run()
    t_brillo = {}
    for aster in files:
        for band in range(10,15):
            calc.gdal_open(aster,band)
            brillo = calc.calc_tbright(band)
            calc.save_aster(aster[:-4],brillo,"tbright",band_number = band)
            calc.gdal_open(aster,band)
            radiancia = calc.rad
            calc.save_aster(aster[:-4],radiancia,"rad",band_number = band)
            print "Banda {} terminada".format(band)
        t_bright = calc.get_tbright(aster[:-4])
        for _brillo in t_bright:
            t_brillo[_brillo[-6:-4]] = calc.gdal_open(_brillo)
        sst = calc.calc_sst(t_brillo["10"],t_brillo["11"],t_brillo["12"],t_brillo["13"],t_brillo["14"],)
        sst2 = calc.calc_sst2(t_brillo["13"],t_brillo["14"])
        calc.gdal_open(_brillo)
        calc.save_aster(aster[:-4],sst,"sst")
        calc.gdal_open(_brillo)
        calc.save_aster(aster[:-4],sst2,"sst2")
        print "Archivo {} terminado".format(aster[:-4])
