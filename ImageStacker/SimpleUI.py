import pygame
from pygame.locals import *

# keys = dict('a',K_A; 'b',K_B;
LETTERS = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
           "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

def waitForKey():
	waiting = True
	while waiting:
		event=pygame.event.wait()
		if event.type == KEYDOWN:
			waiting = False
			return LETTERS[event.key-97]
			"""
			if key_value:
				if event.key == key_value:
					waiting = False
				elif LETTERS[event.key-97] == key_value.upper():
					waiting = False
			else:
				waiting = False
			"""
