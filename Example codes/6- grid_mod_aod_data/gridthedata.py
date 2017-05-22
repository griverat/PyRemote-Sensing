import numpy as np

def grid(limit,gsize,indata,inlat,inlon):
	dx=gsize
	dy=gsize
	minlat=float(limit[0])
	maxlat=float(limit[1])
	minlon=float(limit[2])
	maxlon=float(limit[3])
	xdim=int(1+((maxlon-minlon)/dx))
	ydim=int(1+((maxlat-minlat)/dy))
	sumtau=np.zeros((xdim,ydim))
	sqrtau=np.zeros((xdim,ydim))
	count=np.zeros((xdim,ydim))
	mintau=np.full([xdim,ydim],10)
	maxtau=np.full([xdim,ydim],-1)
	avgtau=np.full([xdim,ydim],-1)
	stdtau=np.full([xdim,ydim],-1)
	grdlat=np.full([xdim,ydim],-1)
	grdlon=np.full([xdim,ydim],-1)
	n=0
	for ii in range(len(indata)):
		if (inlat[ii]>=minlat and inlat[ii] <= maxlat and inlon[ii]>= minlon and inlon[ii] <= maxlon):
			i=round((inlon[ii]-minlon)/dx)
			j=round((inlat[ii]-minlat)/dy)
			sumtau[i,j]=sumtau[i,j]+indata[ii]
			sqrtau[i,j]=sqrtau[i,j]+(indata[ii])**2
			count[i,j]+=1
			if indata[ii] < mintau[i,j]:
				mintau[i,j]=indata[ii]
			if indata[ii] > maxtau[i,j]:
				maxtau[i,j]=indata[ii]
	for i in range(xdim):
		for j in range(ydim):
			grdlon[i,j]=dx*i+minlon
			grdlat[i,j]=dx*j+minlat
			if count[i,j] > 0:
				avgtau[i,j]=sumtau[i,j]/count[i,j]
				para1=(1/count[i,j])*(sqrtau[i,j])+(count[i,j])*avgtau[i,j]-2*(avgtau[i,j])*(sumtau[i,j])
				if para1 > 0:
					stdtau[i,j]=np.sqrt(para1)
	mintau[mintau==10]=-1
	return(avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count)

