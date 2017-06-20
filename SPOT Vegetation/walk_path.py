# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 23:14:48 2017

@author: Gerardo A. Rivera Tello
"""

import os
import time
import combine_files as cf

dirs = []
for path, subdirs, files in os.walk(os.getcwd()):
    if '1.' in path:
        dirs.append(path)

#%%
tif_dir = os.path.join(os.getcwd(),'TIF_Data')
if not os.path.exists(tif_dir):
    os.mkdir(tif_dir)

#%%
for num, path in enumerate(dirs):
    os.chdir(path)
    start_time = time.time()
    hdf_files = [hdf for hdf in os.listdir(os.getcwd()) if hdf.endswith('.HDF')]
    txt_files = [txt for txt in os.listdir(os.getcwd()) if txt.endswith('_LOG.TXT')]
    if 'NDV' in hdf_files[0]:
        print '{}\nComenzando el procesado de {}'.format('='*30,hdf_files[0][:-8])
        cf.main(hdf_files[0],hdf_files[1],txt_files[0],tif_dir)
    else:
        print '{}\nComenzando el procesado de {}'.format('='*30,hdf_files[0][:-8])
        cf.main(hdf_files[1],hdf_files[0],txt_files[0],tif_dir)
    print 'Proceso {} terminado en {} segundos\n'.format(num+1,round(time.time() - start_time,2))