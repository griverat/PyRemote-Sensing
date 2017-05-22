#import necessary modules
from pyhdf import SD
import numpy as np
import gridthedata, h5py
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

#This finds the user's current path so that all hdf4 files can be found
try:
	fileList=np.loadtxt('fileList.txt',dtype='str',delimiter='\t')
except:
	print('Did not find a text file containing file names (perhaps name does not match)')
	sys.exit()
try:
	numOfFiles=len(fileList)
except:
	print('Please use the ARSET module titled "whatever it is", aimed at gridding a single MODIS file.')
	sys.exit()

fileNumber=0
FILE_NAME=str(fileList[fileNumber])[2:-1]
	
if '3K' in FILE_NAME: #then this is a 3km MODIS file
	userInput=int(input('Which SDS would you like to view? (Type the number and press enter) \n(1) Optical_Depth_Land_And_Ocean  \n(2) Image_Optical_Depth_Land_And_Ocean \n'))
	while userInput not in {1,2,3,4}:#repeats the question if the user does not choose one of the options
		print('Please try again.')
		userInput=int(input('Which SDS would you like to view? (Type the number and press enter) \n(1) Optical_Depth_Land_And_Ocean \n(2) Image_Optical_Depth_Land_And_Ocean \n'))
	#Uses a Python dictionary to choose the SDS indicated by the user
	dataFields=dict([(1,'Optical_Depth_Land_And_Ocean'),(2,'Image_Optical_Depth_Land_And_Ocean')])
elif 'L2' in FILE_NAME:#Same as above but for 10km MODIS file
	userInput=int(input('Which SDS would you like to view? (Type the number and press enter) \n(1) Deep_Blue_Aerosol_Optical_Depth_550_Land \n(2) AOD_550_Dark_Target_Deep_Blue_Combined \n'))
	while userInput not in {1,2,3}:
		print('Please try again.')
		userInput=int(input('Which SDS would you like to view? (Type the number and press enter) \n(1) Deep_Blue_Aerosol_Optical_Depth_550_Land \n(2) AOD_550_Dark_Target_Deep_Blue_Combined \n'))
	dataFields=dict([(1,'Deep_Blue_Aerosol_Optical_Depth_550_Land'),(2,'AOD_550_Dark_Target_Deep_Blue_Combined')])
SDS_NAME=dataFields[int(userInput)] # The name of the sds to read
	
dateOfFile=FILE_NAME[10:17]
nextFileName=str(fileList[fileNumber+1])[2:-1]
dateOfNextFile=nextFileName[10:17]
limit=np.zeros(4)
limit[0]=input('\nEnter the minimum latitude of the region you would like to grid: ')
while limit[0] not in range(-90,91):
	print('Please try again.')
	limit[0]=input('Enter the minimum latitude of the region you would like to grid: ')
limit[1]=input('\nEnter the maximum latitude of the region you would like to grid: ')
while limit[1] < limit[0] or limit[1] not in range(-90,91):
	print('Please try again.')
	limit[1]=input('Enter the maximum latitude of the region you would like to grid: ')
limit[2]=input('\nEnter the minimum longitude of the region you would like to grid: ')
while limit[2] not in range(-180,181):
	print('Please try again.')
	limit[2]=input('Enter the minimum longitude of the region you would like to grid: ')
limit[3]=input('\nEnter the maximum longitude of the region you would like to grid: ')
while limit[3]<limit[2] or limit[3] not in range(-180,181):
	print('Please try again.')
	limit[3]=input('Enter the maximum longitude of the region you would like to grid: ')
gridSize=float(input('Please enter the grid size you would like, in degrees (i.e. .5): '))
'''
limit[0]=25
limit[1]=50
limit[2]=-120
limit[3]=-60
gridSize=1
'''
allLat=[]
allLon=[]
allData=[]
for file in range(numOfFiles):
	FILE_NAME=str(fileList[file])[2:-1]
	try:
		# open the hdf file for reading
		hdf=SD.SD(FILE_NAME)
	except:
		print('Unable to open file: \n' + FILE_NAME + '\n Skipping...')
		continue
		
	# Get lat and lon info
	lat = hdf.select('Latitude')
	latitude = lat[:,:]
	lon = hdf.select('Longitude')
	longitude = lon[:,:]
	
	#get SDS, or exit program if SDS is not in the file
	try:
		sds=hdf.select(SDS_NAME)
	except:
		try:
			sds=hdf.select('Optical_Depth_Land_And_Ocean')
		except:
			print('Sorry, your MODIS hdf file does not contain the SDS:',SDS_NAME,'. Please try again with the correct file type.')
			continue
		
	#get scale factor and fill value for data field
	attributes=sds.attributes()
	scale_factor=attributes['scale_factor']
	fillvalue=attributes['_FillValue']
	range=attributes['valid_range']
	#get SDS data
	data=sds.get()
	#get SDS data
	min_range=min(range)*scale_factor
	max_range=max(range)*scale_factor
	
	#get data within valid range
	valid_data=data*scale_factor
	valid_data=valid_data.flatten()
	latitude=latitude.flatten()
	longitude=longitude.flatten()
	valid_data[valid_data<=min_range]=-9999
	valid_data[valid_data>=max_range]=-9999
	longitude=longitude[valid_data>-100]
	latitude=latitude[valid_data>-100]
	valid_data=valid_data[valid_data>-100]
	latitude[latitude<limit[0]]=-9999
	latitude[latitude>limit[1]]=-9999
	longitude[latitude<0]=-9999
	longitude[longitude<limit[2]]=-9999
	longitude[longitude>limit[3]]=-9999
	latitude=latitude[longitude>-200]
	valid_data=valid_data[longitude>-200]
	longitude=longitude[longitude>-200]
	if len(allData) == 0:
		allLat=latitude
		allLon=longitude
		allData=valid_data
		
	elif len(allData)>0:
		allLat=np.concatenate((allLat,latitude),axis=1)
		allLon=np.concatenate((allLon,longitude),axis=1)
		allData=np.concatenate((allData,valid_data),axis=1)

print('Gridding ',file+1,'MODIS files...')
avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count=gridthedata.grid(limit,gridSize,allData,allLat,allLon)

is_map=str(input('\nWould you like to create a map of this data? Please enter Y or N \n'))
#if user would like a map, view it
if is_map == 'Y' or is_map == 'y':
	data=avgtau
	data[data == -1] = np.nan
	#create the map
	data = np.ma.masked_array(data, np.isnan(data))
	m = Basemap(projection='cyl', resolution='l', llcrnrlat=min(grdlat.flatten()), urcrnrlat = max(grdlat.flatten()), llcrnrlon=min(grdlon.flatten()), urcrnrlon = max(grdlon.flatten()))
	m.drawcoastlines(linewidth=0.5)
	m.drawparallels(np.arange(-90., 120., 5), labels=[1, 0, 0, 0])
	m.drawmeridians(np.arange(-180., 181., 5.), labels=[0, 0, 0, 1])
	x, y = m(grdlon, grdlat)
	m.pcolormesh(x, y, data)
	plt.autoscale()
	#create colorbar
	cb = m.colorbar()
	cb.set_label('AOD')
	
	#title the plot
	saveTitle='FILE_NAME[:-4]'
	plt.title('{0}\n {1}'.format(SDS_NAME,'Gridded at ' + str(gridSize) + ' Degrees Using ' + str(file+1) + ' Files'))
	fig = plt.gcf()
	# Show the plot window.
	plt.show()
	#once you close the map it asks if you'd like to save it
	is_save=str(input('\nWould you like to save this map? Please enter Y or N \n'))
	if is_save == 'Y' or is_save == 'y':
		#saves as a png if the user would like
		pngfile = '{0}.png'.format(saveTitle)
		fig.savefig(pngfile)
		
is_save=input('\nWould you like to save the gridded data as an HDF5 file? Please enter Y or N \n')
if is_save == 'Y' or is_save =='y':
	avgtau[avgtau==-1]=-9999
	stdtau[stdtau==-1]=-9999
	mintau[mintau==10]=-9999
	maxtau[maxtau==-1]=-9999
	print('Writing HDF5 file...')
	#write out to hdf5 file
	h5Out=h5py.File('griddedData.h5','w')
	gridded=h5Out.create_group('Aerosol Gridded Data')
	avg=gridded.create_dataset('griddedAverage',avgtau.shape,'f')
	avg[:,:]=avgtau[:,:]
	std=gridded.create_dataset('griddedStandardDeviation',stdtau.shape,'f')
	std[:,:]=stdtau[:,:]
	min=gridded.create_dataset('griddedMinimum',mintau.shape,'f')
	min[:,:]=mintau[:,:]
	max=gridded.create_dataset('griddedMaximum',maxtau.shape,'f')
	max[:,:]=maxtau[:,:]
	cnt=gridded.create_dataset('griddedCount',count.shape,'f')
	cnt[:,:]=count[:,:]
	for data in gridded:
		gridded[data].attrs['FillValue']=-9999
		gridded[data].attrs['ScaleFactor']=1
		gridded[data].attrs['Units']='None'
		gridded[data].attrs['Add_offset']='None'
	geolocation=h5Out.create_group('Geolocation')
	lat=geolocation.create_dataset('Latitude',grdlat.shape,'f')
	lat[:,:]=grdlat[:,:]
	lat.attrs['ScaleFactor']=1
	lat.attrs['Valid_Range']='-90,90'
	lat.attrs['Units']='Degrees North'
	lon=geolocation.create_dataset('Longitude',count.shape,'f')
	lon[:,:]=grdlon[:,:]
	lon.attrs['ScaleFactor']=1
	lon.attrs['Valid_Range']='-180,180'
	lon.attrs['Units']='Degrees East'
	
	
	
	
	
	
	
