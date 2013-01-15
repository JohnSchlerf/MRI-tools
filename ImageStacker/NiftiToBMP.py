#!/usr/bin/python

# This is a little optimistic for today...

import nifti
import sys
from pylab import *
import matplotlib.pyplot as plt

from SimpleUI import *
from Monitor import *

screen = Monitor(1,1,False,0,mouseVisible=1)

def show_image(UL,OL1,OL1t,OL2,OL2t):
	fig = figure(1)
	ax1 = fig.add_subplot(1,1,1)
	B = ax1.imshow(UL[:,:,50],cmap=cm.gray,origin='lower')
	
	ax1.imshow(OL1[:,:,50],cmap=cm.hot,vmin=OL1t[0],vmax=OL1t[1],origin='lower')
	if OL2:
		ax1.imshow(OL2[:,:,50],cmap=cm.cool,vmin=OL2t[0],vmax=OL2t[1],origin='lower')
	fig.show()
	plt.draw()
	plt.show()
	
# parse my inputs:
underlay = sys.argv[1]
overlay1 = sys.argv[2]
overlay1thresh = [float(sys.argv[3]),float(sys.argv[4])]
try:
	overlay2 = sys.argv[5]
	overlay2thresh = [float(sys.argv[6]),float(sys.argv[7])]
except:
	overlay2 = None
	overlay2thresh = None

# load my nifti files:

UL = nifti.niftiimage.NiftiImage(underlay)
ULd = UL.asarray()
OL1 = nifti.niftiimage.NiftiImage(overlay1)
OL1d = OL1.asarray()
if overlay2:
	OL2 = nifti.niftiimage.NiftiImage(overlay2)
	OL2d = OL2.asarray()
else:
	OL2d = None
show_image(ULd,OL1d,overlay1thresh,OL2d,overlay2thresh)
screen.close()
#self.ax1.imshow(self.Image[self.time,:,:,self.z],cm.gray,vmin=self.vmin,vmax=self.vmax,origin='lower')
