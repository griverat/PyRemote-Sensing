#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 15:22:35 2017

@author: DangoMelon0701
"""
import os

for filename in os.listdir(os.getcwd()):
    if filename.startswith("AVHRR"):
        os.rename(filename,"{}.nc".format(filename[:-3]))