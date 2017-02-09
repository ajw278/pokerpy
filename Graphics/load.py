"""=================================================================================================
//  POKERPY :
//  Python code for automated poker learning and playing.
//  https://github.com/ajw278/pokerpy.git
//  Contact : ajwinter@ast.cam.ac.uk
//  Contributors : Andrew Winter, Pablo Lemos Portela, Cameron Lemon
//  Description : 
//
//  Last edited: 20/12/2016
//================================================================================================="""

from __future__ import print_function

import os
import sys
import pygame

scriptpath = os.path.dirname(os.path.realpath(__file__))


def load_img(name):
	""" Load image and return image object"""
	fullname = os.path.join(scriptpath+'/graphic_data', name)
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
