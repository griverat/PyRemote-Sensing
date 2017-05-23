#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 13:23:10 2017

@author: Gerardo A. Rivera Tello
"""
import os
import numpy as np
from struct import unpack

class Reorder_bin(object):
    def __init__(self):
        pass
    
    def read_chunk(self,block,data,offset,n_elements,data_type):
        #Read the data decoded inside of the file object data. 
        #It returns a tuple containing the type of data specified
        #Set block to 1 to read a single value (type 'i' or 'f')
        #Set block to 0 to read into a numpy array (numpy dtype)
        data.seek(offset)
        if block==1:
            rdata = data.read(n_elements)
            return unpack(data_type,rdata)[0]
        elif block==0:
            rdata = np.fromfile(data,dtype=data_type,count=n_elements)
            return rdata
    
    def write_to_bin(self,bin_to_write,hdr,data):
        #Write the data specified with a header indicating the size in the
        #begining and the end of the record
        bin_to_write.write(hdr.to_bytes(4,byteorder='big'))
        data.astype(np.float32).tofile(bin_to_write)
        bin_to_write.write(hdr.to_bytes(4,byteorder='big'))
    
    def reorder_bin(self,bin_file,nlines,nsamples,nsteps):
        #Call to reorder the binary file into something GrADS can read
        #i.e. remove the end of line headers indicating the size, leaving
        #only the initial and final header of a whole day record
        with open(bin_file,'rb') as in_bin, open('reord_{}'.format(bin_file),'ab') as out_bin:
            initial_offset=0
            for t_steps in range(nsteps):
                for lines in range(nlines):
                    inum_bytes_data = self.read_chunk(1,in_bin,initial_offset,4,'i')
                    
                    if lines == 0:
                        real_data = self.read_chunk(0,in_bin,initial_offset+4,int(inum_bytes_data/8),np.float64)
                    else:
                        real_data = np.vstack((real_data,self.read_chunk(
                            0,in_bin,initial_offset+4,int(inum_bytes_data/8),np.float64)))

                    fnum_bytes_data = self.read_chunk(1,in_bin,initial_offset+inum_bytes_data+4,4,'i')
                    initial_offset = (t_steps*320+lines+1)*(8+inum_bytes_data)
                self.write_to_bin(out_bin,fnum_bytes_data,real_data)

if __name__ == '__main__':
    files_list = []
    for files in os.listdir(os.getcwd()):
        if files.endswith('.bin'):
            files_list.append(files)
    for binfile in files_list:
        unord_bin = Reorder_bin()
        unord_bin.reorder_bin(binfile,320,720,24)