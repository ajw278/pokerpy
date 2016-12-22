from __future__ import print_function

import os
import sys
import pygame


def load_img(name):
	""" Load image and return image object"""
	fullname = os.path.join('graphic_data', name)
	try:
		image = pygame.image.load(fullname)
		if image.get_alpha() is None:
			image = image.convert()
		else:
			image = image.convert_alpha()
	except pygame.error, message:
        	print('Cannot load image:', fullname)
		sys.exit()
	return image, image.get_rect()
