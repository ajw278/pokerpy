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

#pokerface.py
#pygame interface

from __future__ import print_function

import menu

import sys
import random
import math
import os
import getopt
import pygame
from socket import *
#from menu import *
from pygame.locals import *

#Colours
BLACK = (  0,   0,   0)
TRANSP = (0, 0, 0, 0)
WHITE = (255, 255, 255)
RED = (255,   0,   0)
GREEN = (  0, 255,   0)
DARKERGREEN = (50, 200, 50)
BLUE = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
DARKRED = (100,   0,   0)

EVENT_CHANGE_STATE = pygame.USEREVENT + 1


def textobj(message, size, position):
	fontObj = pygame.font.Font('./Fonts/Alien_League.ttf', size)
	textObj = fontObj.render(message, 1, DARKERGREEN)
	textRect = textObj.get_rect()
	textRect.midtop = position
	return textObj, textRect

def terminate():
	pygame.quit()
	sys.exit()


def main():
	#____________________Set constants of the game______________________________#

	pygame.init()

	#Frames per second setting
	FPS = 30

	#_____________________________Game Initialisation________________________________#

	fpsClock = pygame.time.Clock()

	#Initialise window
	infoObj = pygame.display.Info()
	SCW = infoObj.current_w
	SCH = infoObj.current_h
	DISPLAYSURF = pygame.display.set_mode((SCH, SCH), pygame.FULLSCREEN, 32)
	SCRECT = DISPLAYSURF.get_rect()
	pygame.display.set_caption('PokerPy')
	SCW =SCH
	CENTER = (SCW/2, SCH/2)
	#FPS = FPS* float(SCH)/1200.
	#_________________________________Formatting_______________________________#
	#Colours
	BLACK = (  0,   0,   0)
	TRANSP = (0, 0, 0, 0)
	WHITE = (255, 255, 255)
	RED = (255,   0,   0)
	GREEN = (  0, 255,   0)
	DARKERGREEN = (50, 200, 50)
	BLUE = (  0,   0, 255)
	YELLOW   = (255, 255,   0)
	ORANGE   = (255, 128,   0)
	PURPLE   = (255,   0, 255)
	CYAN     = (  0, 255, 255)
	DARKRED = (100,   0,   0)

	#Assign fonts
	SMALLTEXT = SCH/30
	MIDTEXT = SCH/25
	LARGETEXT = SCH/15
	MASSIVETEXT = SCH/8
	titlefontObj = pygame.font.Font('./Fonts/Alien_League.ttf', 75)
	levelfontObj = pygame.font.Font('./Fonts/Alien_League.ttf', 26)

	mbg = pygame.image.load("./graphic_data/MainBG.jpg")
	mbg = pygame.transform.scale(mbg, (SCW, SCH))

	# Create 3 diffrent menus.  One of them is only text, another one is only
	# images, and a third is -gasp- a mix of images and text buttons!  To
	# understand the input factors, see the menu file
	main_menu = menu.cMenu(SCW/2-int(float(LARGETEXT)*2.5), 2*SCH/7, 20, 5, 'vertical', 100, DISPLAYSURF,
	       [('Play Poker', 1, None),
		('Training', 3, None),
		('Settings', 4, None),
		('Data',  2, None),
		('Exit',       5, None)], TRANSP, LARGETEXT)

	# Center the menu on the draw_surface (the entire screen here)
	#main_menu.set_center(False, False)

	main_menu.set_alignment('center', 'center')

	GAMESTATE = 'menu'
	
	titletextX = SCW/2
	titletextY = SCH/8
	titletextSurfaceObj, titletextRectObj = textobj('POKERPY' , MASSIVETEXT, (titletextX, titletextY))
	titletextRectObj.center = (titletextX, titletextY) 
	
	# rect_list is the list of pygame.Rect's that will tell pygame where to
	# update the screen 
	rect_list = []
	# Ignore mouse motion (greatly reduces resources when not needed)
	pygame.event.set_blocked(pygame.MOUSEMOTION)

	#Menu state variables
	state = 0
	prev_state = 1

	while True:
		for e in pygame.event.get():
			if (e.type is pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
				toggle_fullscreen()

		if GAMESTATE == 'menu':
			if prev_state != state:
				DISPLAYSURF.blit(mbg, (CENTER[0]-SCW/2,CENTER[1]-SCH/2))
				DISPLAYSURF.blit(titletextSurfaceObj, titletextRectObj)
				pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key = 0))
				prev_state = state

			# Get the next event
			e = pygame.event.wait()

			# Update the menu, based on which "state" we are in 
			if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
				if state == 0:
					rect_list, state = main_menu.update(e, state)
				elif state == 1:
					flag=0	
					state = 0
				elif state == 2:
					flag=0	
					state =0
				elif state ==3:
					flag=0	
					state =0
				elif state ==4:
					flag=0
					state=0
				else:
					state=0
					terminate()

			# Quit if the user presses the exit button
			if e.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			# Update the screen
			pygame.display.update(rect_list)

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		pygame.display.update()
		fpsClock.tick(FPS)

	return 0


if __name__ == '__main__':
    main()
