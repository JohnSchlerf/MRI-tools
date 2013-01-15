#!/usr/bin/python

# Little tool created to edit the automatic cerebellar segmentation 
# generated by SUIT_isolate. Edits the binary mask saved as a nifti file, 
# and saves the resulting segmentation. This edited segmentation can be 
# used to improve the results of SUIT_normalize.
# (see http://www.icn.ucl.ac.uk/motorcontrol/imaging/suit.htm)
#
# Written by John Schlerf, 2010

# Updated to not crash if used to make other ROIs (ie, not starting with
# the default SUIT *_pcereb_corr image).
#
#  - John Schlerf, November 13, 2010

import nifti

try:
	from nifti import niftiimage as image
	nifti.image = image
except:
	None

import sys
import glob # Do I need glob?
from pylab import *
from copy import copy
import matplotlib.pyplot as plt

# I hate hate HATE using Caret for SUIT ROI cleanup. What I want to do 
# instead is use a simple python GUI to do it nicely. So, here's my
# attempt to do that.

class Python_3D_View:
	penthickness = 1
	time = 0
	view = 'sagittal'
	MoveEventArray = []
	overlayOn = True
	toggleable = True
	imageSaved = False
	
	def __init__(self,anat_image,overlay_image,outputname):
		self.flippable = True # I don't know what this is.
		# Assuming this makes it a 4D image
		anat_data = anat_image.asarray()
		self.determine_flip(anat_image.header['sform'])
		if len(anat_data.shape) == 4:
			self.Image = anat_data
		else:
			self.Image = anat_data.reshape([1,anat_data.shape[0],anat_data.shape[1],anat_data.shape[2]])
		self.olay_image = overlay_image
		olay_data = overlay_image.asarray()
		if len(olay_data.shape) == 4:
			self.Olay = olay_data
		else:
			self.Olay = olay_data.reshape([1,olay_data.shape[0],olay_data.shape[1],olay_data.shape[2]])
		
		# If we loaded the anatomical as the overlay, then blank it:
		if (self.Image == self.Olay).all():
			self.Olay = 0*self.Olay

		self.outputname = outputname

		self.flip_data()

		self.num_times = self.Image.shape[0]
		self.num_slices = {'coronal':self.Image.shape[2],
				   'sagittal':self.Image.shape[3],
				   'axial':self.Image.shape[1]}

		self.slice = {'coronal':self.Image.shape[2]/2,
			      'sagittal':self.Image.shape[3]/2,
			      'axial':self.Image.shape[1]/2}

		self.vmin = self.Image.min()
		self.vmax = self.Image.max()
		
		self.fig = figure(1)
		self.fig.canvas.mpl_connect('button_press_event',self.click_event)
		self.fig.canvas.mpl_connect('button_release_event',self.unclick_event)
		self.fig.canvas.mpl_connect('key_press_event',self.key_press_callback)
		self.fig.canvas.mpl_connect('motion_notify_event',self.move_event)
		self.fig.canvas.mpl_connect('scroll_event',self.scroll_event)
				
		self.ax1 = self.fig.add_subplot(3,4,1)
		self.ax1.set_position([0.125,0.125,0.5,0.75])
		self.ax1.axis('off')
		
		self.ax2 = self.fig.add_subplot(3,4,4)
		self.ax2.axis('off')
		
		self.ax3 = self.fig.add_subplot(3,4,8)
		self.ax3.axis('off')
		
		self.ax4 = self.fig.add_subplot(3,4,12)
		self.ax4.axis('off')
				
		self.ax1.hold('on')
		self.ax2.hold('on')
		self.ax3.hold('on')
		self.ax4.hold('on')
		
		self.ax1im = self.ax1.imshow(zeros((max(self.Image.shape),max(self.Image.shape))),
					     cm.gray,interpolation='nearest',vmin=self.vmin,vmax=self.vmax,origin='lower')
		self.ax2im = self.ax2.imshow(self.Image[0,:,:,self.slice['sagittal']],
					     cm.gray,vmin=self.vmin,vmax=self.vmax,origin='lower')
		self.ax3im = self.ax3.imshow(self.Image[0,:,self.slice['coronal'],:],
					     cm.gray,vmin=self.vmin,vmax=self.vmax,origin='lower')
		self.ax4im = self.ax4.imshow(self.Image[0,self.slice['axial'],:,:],
					     cm.gray,vmin=self.vmin,vmax=self.vmax,origin='lower')
		
		self.ax1ol = self.ax1.imshow(zeros((max(self.Image.shape),max(self.Image.shape))),
					     cm.Reds,interpolation='nearest',alpha=0.6,origin='lower',vmin=0,vmax=1)
		self.ax2ol = self.ax2.imshow(self.Image[0,:,:,self.slice['sagittal']],
					     cm.Reds,interpolation='nearest',alpha=0.6,origin='lower',vmin=0,vmax=1)
		self.ax3ol = self.ax3.imshow(self.Image[0,:,self.slice['coronal'],:],
					     cm.Reds,interpolation='nearest',alpha=0.6,origin='lower',vmin=0,vmax=1)
		self.ax4ol = self.ax4.imshow(self.Image[0,self.slice['axial'],:,:],
					     cm.Reds,interpolation='nearest',alpha=0.6,origin='lower',vmin=0,vmax=1)
		
		self.re_plot()
	
	def determine_flip(self,sform):
		# Yeah... duh!
		EyeNotQuite = abs(sform.round())
		if (EyeNotQuite[0,0] == 1) and (EyeNotQuite[1,1] == 1) and (EyeNotQuite[2,2] == 1):
			self.flip = None
		elif (EyeNotQuite[0,2] == 1) and (EyeNotQuite[1,0] == 1) and (EyeNotQuite[2,1] == 1):
			self.flip = 'Berkeley_Siemens'
		else:
			# Adding this for my own debugging, thought it's a bit of a hack...
			self.flip = None
		None
	
	def flip_data(self):
		
		if self.flip == 'Berkeley_Siemens':
			# This is probably going to be reproduceable, so...
			self.Image = self.Image.transpose((0,2,3,1))
			self.Olay = self.Olay.transpose((0,2,3,1))
			self.Image = self.Image[:,:,::-1,:]
			self.Olay = self.Olay[:,:,::-1,:]
			
		# Apply my flip
		#self.Image
		#self.Olay

	def unflip_data(self):
		if self.flip == 'Berkeley_Siemens':
			# Do my unflippin'
			self.Image = self.Image[:,:,::-1,:]
			self.Olay = self.Olay[:,:,::-1,:]
			self.Image = self.Image.transpose((0,3,1,2))
			self.Olay = self.Olay.transpose((0,3,1,2))
			
			
	def re_plot_helpers(self):
		None

	def re_plot(self):
		# Deal with main window:
		if self.view == 'coronal':
			anatslice = self.Image[0,:,self.slice['coronal'],:]
			olayslice = self.Olay[0,:,self.slice['coronal'],:]
		elif self.view == 'sagittal':
			anatslice = self.Image[0,:,:,self.slice['sagittal']]
			olayslice = self.Olay[0,:,:,self.slice['sagittal']]
		elif self.view == 'axial':
			anatslice = self.Image[0,self.slice['axial'],:,:]
			olayslice = self.Olay[0,self.slice['axial'],:,:]
		self.ax1im.set_data(anatslice)
		
		# Now do overlays as a masked array:
		if self.overlayOn:
			olay = ma.array(olayslice,mask=olayslice==0)
		else:
			olay = ma.array(olayslice,mask=olayslice==olayslice)
		self.ax1ol.set_data(olay)

		###############################################################
		# Saved / Not Saved warning:
		if self.imageSaved:
			self.ax1.set_title('Everything is now OK. Saved as ' + self.outputname)
		else:
			self.ax1.set_title('Not saved.  Press S to save as ' + self.outputname)
		
		###############################################################
		# OK, now deal with the three other windows, image and overlay (if visible)
		
		# Sagittal stamp view
		self.ax2im.set_data(self.Image[0,:,:,self.slice['sagittal']])
		if self.overlayOn:
			self.ax2ol.set_data(ma.array(self.Olay[0,:,:,self.slice['sagittal']],mask=self.Olay[0,:,:,self.slice['sagittal']]==0))
		else:
			self.ax2ol.set_data(ma.array(zeros((10,10)),mask=zeros((10,10))==0))

		# Coronal stamp view
		self.ax3im.set_data(self.Image[0,:,self.slice['coronal'],:])
		if self.overlayOn:
			self.ax3ol.set_data(ma.array(self.Olay[0,:,self.slice['coronal'],:],mask=self.Olay[0,:,self.slice['coronal'],:]==0))
		else:
			self.ax3ol.set_data(ma.array(zeros((10,10)),mask=zeros((10,10))==0))
		
		# Axial stamp view
		self.ax4im.set_data(self.Image[0,self.slice['axial'],:,:])
		if self.overlayOn:
			self.ax4ol.set_data(ma.array(self.Olay[0,self.slice['axial'],:,:],mask=self.Olay[0,self.slice['axial'],:,:]==0))
		else:
			self.ax4ol.set_data(ma.array(zeros((10,10)),mask=zeros((10,10))==0))
		
		draw()

	def scroll_event(self, event):
                self.slice[self.view] += event.step
		if self.slice[self.view] < 0:
			self.slice[self.view] = 0
		elif self.slice[self.view] >= self.num_slices[self.view]:
			self.slice[self.view] = self.num_slices[self.view]-1
		self.re_plot()

	def unclick_event(self, event):
		for ev in self.MoveEventArray:
			self.edit(ev[0],ev[1],ev[2])
		self.MoveEventArray = []
		self.re_plot()
		self.toggleable = True
		None
		
		#self.flippable = True

	def save_data(self):
		#nifti_image = nifti.niftiimage.NiftiImage(self.Olay,header=self.olay_image.header)
		self.unflip_data()
		nifti_image = nifti.image.NiftiImage(self.Olay,header=self.olay_image.header)
		nifti_image.save(self.outputname)
		self.imageSaved = True
		self.flip_data()
		self.re_plot()

	def edit(self,which,x,y):
		
		if self.overlayOn:
			# Only edit if the overlays are visible
			# Find the voxel:
			xymax = max(self.Image.shape)
			if self.view == 'sagittal':
				corcoord = round(x)
				axcoord = round(y)
				sagcoord = self.slice['sagittal']
			elif self.view == 'coronal':
				corcoord = self.slice['coronal']
				axcoord = round(y)
				sagcoord = round(x)
			elif self.view == 'axial':
				corcoord = round(y)
				sagcoord = round(x)
				axcoord = self.slice['axial']
			
			if (corcoord > self.num_slices['coronal']-1) or \
				    (sagcoord > self.num_slices['sagittal']-1) or \
				    (axcoord > self.num_slices['axial']-1) or \
				    (corcoord < 0) or \
				    (sagcoord < 0) or \
				    (axcoord < 0):
				None
			else:
				if which=='remove':
					self.draw_values(axcoord,corcoord,sagcoord,0)
				elif which=='add':
					self.draw_values(axcoord,corcoord,sagcoord,1)

	def draw_values(self,ax,cor,sag,val):
		L = -self.penthickness
		R = self.penthickness
		[x,y] = mgrid[L:R,L:R]
		x = x.flatten()
		y = y.flatten()
		rad = sqrt(x**2+y**2)
		if self.view == 'sagittal':
			C = x[rad<self.penthickness] + cor
			A = y[rad<self.penthickness] + ax
			S = zeros(len(C)) + sag
		elif self.view == 'axial':
			C = x[rad<self.penthickness] + cor
			A = zeros(len(C)) + ax
			S = y[rad<self.penthickness] + sag
		elif self.view == 'coronal':
			A = y[rad<self.penthickness] + ax
			C = zeros(len(A)) + cor
			S = x[rad<self.penthickness] + sag

		for i in range(len(C)):
			c = C[i]
			s = S[i]
			a = A[i]
			if (c > self.num_slices['coronal']-1) or \
				    (s > self.num_slices['sagittal']-1) or \
				    (a  > self.num_slices['axial']-1) or \
				    (c < 0) or \
				    (s < 0) or \
				    (a  < 0):
				None #print "out"
			else:
				self.imageSaved = False
				self.Olay[0,a,c,s] = val

	def move_event(self,event):
		# Really, I only care about this for drawing:
		if self.ax1.contains(event)[0]:
			x = event.xdata
			y = event.ydata
			if event.button == 1:
				item = ['add',x,y]
			elif event.button == 3:
				item = ['remove',x,y]
			else:
				item = []
			if not(item in self.MoveEventArray) and (len(item)>0):
				self.MoveEventArray.append(item)
			
	def key_press_callback(self,event):
		if event.key in ['d','D']:
			self.edit('DeleteChunk',event.xdata,event.ydata)
		elif event.key in ['s','S']:
			self.save_data()
			print "Save"
		elif event.key in ['-','_']:
			self.penthickness -= 1
			if self.penthickness < 1:
				self.penthickness = 1

		elif event.key in ['=','+']:
			self.penthickness += 1
			if self.penthickness > 5:
				self.penthickness = 5

		elif event.key in ['r','R']:
			print "Revert not available"
		elif event.key in ['u','U','z','Z']:
			print "Undo not available"

	def click_event(self, event):
		
		if self.ax1.contains(event)[0]:
			if event.button==1:
				self.edit('add',event.xdata,event.ydata)
				#self.overlayOn = True
			elif event.button==3:
				self.edit('remove',event.xdata,event.ydata)
				#self.overlayOn = False
			elif event.button==2:
				None
			self.re_plot()

		elif event.button == 1:
			if self.ax2.contains(event)[0]:
				self.view = 'sagittal'
				self.slice['coronal']=int(event.xdata)
				self.slice['axial']  =int(event.ydata)
                                #self.x = int(event.ydata)
				#self.z = int(event.xdata)

			elif self.ax3.contains(event)[0]:
				self.view = 'coronal'
				self.slice['sagittal']=int(event.xdata)
				self.slice['axial']   =int(event.ydata)

			elif self.ax4.contains(event)[0]:
				self.view = 'axial'
				self.slice['sagittal']=int(event.xdata)
				self.slice['coronal'] =int(event.ydata)
				#self.time = int(event.xdata)
			elif self.toggleable:
				self.overlayOn = not(self.overlayOn)
				self.toggleable = False
			self.re_plot()

		elif event.button == 2:
			self.vmin = self.Image.min() + (self.Image.max() - self.Image.min()) * event.x/(self.fig.get_figwidth() * self.fig.get_dpi())
			self.vmax = self.Image.max() - (self.Image.max() - self.Image.min()) * event.y/(self.fig.get_figheight() * self.fig.get_dpi())
			if self.vmin >= self.vmax:
				self.vmin = self.vmax - 1
			self.re_plot()
		#if not(event.button == 0): self.re_plot()



if __name__ == "__main__":
    
	#try:
		# Parse the input:
		Images = sys.argv[1:]
		try:
			Anatomical = Images[0]
		except:
			print "Please give at least an anatomical image as input. Perhaps you could use sample.nii"
			exit()

		try:
			Mask = Images[1]
		except:
			Mask = Anatomical.replace('.nii','_pcereb_corr.nii')
			print "Guessing the mask image... trying " + Mask

		try:
			Output = Images[2]
		except:
			Output = Mask.replace('corr','handcorr')
			print "Output will be saved as " + Output

		# OK, now I've got my input... and, well, maybe that should've been a 
		# function? Whatever.

		#anat_image = nifti.niftiimage.NiftiImage(Anatomical)
		anat_image = nifti.image.NiftiImage(Anatomical)
		
                #anat_data = anat_image.asarray()
		#mask_image = nifti.niftiimage.NiftiImage(Mask)
		try:
			mask_image = nifti.image.NiftiImage(Mask)
		except:
			# If this image doesn't exist, make a copy of the anatomical; when debugged, this turns out to be blank
			mask_image = copy(anat_image)
			
		#mask_data = mask_image.asarray()
		#out_image = nifti.niftiimage.NiftiImage(Output)
		
		Python_3D_View(anat_image,mask_image,Output)
		
		plt.draw()
		plt.show()

	#except:
	#	print "Usage: Coming Soon!"
