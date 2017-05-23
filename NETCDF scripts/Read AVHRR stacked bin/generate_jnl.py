#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 15:31:20 2017

@author: DangoMelon0701
"""
import os
template = 'SET MEMORY/SIZE=100\nuse {}\nset var/bad=999.0 SST\nlist{}/file="sst.bin"/format="unformatted"/I=1:1440/J=1:720/order=xy/nohead SST\n\n'

n=0
files_list=[]
for files in os.listdir(os.getcwd()):
    if files.endswith(".nc"):
        files_list.append(files)
files_list.sort()

with open("descriptor.jnl","w") as jnl_file:
    for nc_file in files_list:
        if n == 0:
            jnl_file.write(template.format(nc_file,""))
            n=1
        else:
            jnl_file.write(template.format(nc_file,"/append"))