#!/usr/bin/python

from Monitor import *
from SimpleUI import *
import sys
import os

def drawStuff(screen,imageObjects,ycoords):
	indices = range(len(imageObjects))
	indices.reverse()
	for index in indices:
		screen.drawObject(imageObjects[index],(max_width/2,ycoords[index]))
	screen.draw()

directory = sys.argv[1]
outputfilename = sys.argv[2]
try:
	overlap = float(sys.argv[3])
except:
	overlap = 0.5

possiblefiles = os.listdir(directory)
imagefiles = []
imageextensions = ['.bmp','.jpg','.png','.gif']

# throw out non-image files
for possiblefile in possiblefiles:
	for ext in imageextensions:
		if ext in possiblefile:
			imagefiles.append(possiblefile)

imagefiles.sort(reverse=True)
imageObjects = []
initial_screen = Monitor(height=10,width=10,fullscreen=False)

for image in imagefiles:
	imageObjects.append(loadImage(os.path.join(directory,image)))

initial_screen.close()

max_height = 0;
max_width = 0;

y_coord = []

for object in imageObjects:
	[width,height] = object.get_size()
	y_coord.append(height*0.5+max_height)
	if width > max_width:
		max_width = width
	max_height += height * overlap

# one more to get the bottom visible:
max_height += height*(1-overlap)

screen = Monitor(height=int(max_height),width=max_width,fullscreen=False,grabValue=0,mouseVisible=1)

drawStuff(screen,imageObjects,y_coord)

running = True
while running:
	letter = waitForKey()
	if letter == 'R':
		drawStuff(screen,imageObjects,y_coord)
	elif letter == 'Q':
		running = False

screen.saveScreenShot(outputfilename)
screen.close()
