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
import click_menu


import sys
import random
import math
import os
import getopt
import pygame
from socket import *
#from menu import *
from pygame.locals import *
from collections import namedtuple


import sys
scriptpath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, scriptpath+'/../')
sys.path.insert(0, scriptpath+'/../Odds/')
sys.path.insert(0, scriptpath+'/../Objects/')
sys.path.insert(0, scriptpath+'/../Data/')
import gameplay
import im_objects
import hand
import pokerpy
import random
import player
import table
import saveloadpkl
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

#Graphics dictionary - for the names of the card files
KIND_DICT = {0: 'd', 1:'c',2:'h',3:'s'}
VALUE_DICT = {0: 2, 1: 3, 2: 4, 3: 5, 4:6, 5:7,6:8,7:9,8:10,9:'j', 10:'q',11:'k',12:'a'}

EVENT_CHANGE_STATE = pygame.USEREVENT + 1


def textobj(message, size, position):
	fontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', size)
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
	DISPLAYSURF = pygame.display.set_mode((SCH, SCH))# pygame.FULLSCREEN, 32)
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
	titlefontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', LARGETEXT)
	levelfontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', MIDTEXT)
	textfontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', SMALLTEXT)

	mbg = pygame.image.load(scriptpath+"/graphic_data/MainBG.jpg")
	mbg = pygame.transform.scale(mbg, (SCW, SCH))

	
	GAMESTATE = 'menu'
	
	titletextX = SCW/2
	titletextY = SCH/8
	titletextSurfaceObj, titletextRectObj = textobj('POKERPY' , MASSIVETEXT, (titletextX, titletextY))
	titletextRectObj.center = (titletextX, titletextY) 
	
	# rect_list is the list of pygame.Rect's that will tell pygame where to
	# update the screen 
	rect_list = []
	# Ignore mouse motion (greatly reduces resources when not needed)

	#Menu state variables
	state = 0

	#Load defaults would be done here - set them for now
	nplayers = 2
	pplayers = 0

	chips0 = 400
	mindiff=5
	extrachips=0

	blinds = [10, 20]

	gtype='std'

	while True:
		for e in pygame.event.get():
			if (e.type is pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
				pygame.display.toggle_fullscreen()

		if GAMESTATE == 'menu':
			menu_items = ('Start', 'Load', 'Quit')
			gm = click_menu.GameMenu(DISPLAYSURF, menu_items, bg_color=DARKERGREEN, 
				font=scriptpath+'/Fonts/Alien_League.ttf', font_size=LARGETEXT, font_color=GREEN)
			selection = gm.run()
			if selection==menu_items[0]:
				GAMESTATE='gamesetup'
			if selection==menu_items[1]:
				try:
					game_state = saveloadpkl.load_obj('saved_game',loc=scriptpath+'/../Data/SaveGames/')
					state = game_state.state
					GAMESTATE='play'
				except:
					print('No save data found.')
					GAMESTATE='menu'
			if selection==menu_items[2]:
				sys.exit()
		elif GAMESTATE=='gamesetup':
			menu_items = ('Play', 'Number Players', 'Starting Bank', 'Quit')
			gm = click_menu.GameMenu(DISPLAYSURF, menu_items, bg_color=DARKERGREEN, 
				font=scriptpath+'/Fonts/Alien_League.ttf', font_size=LARGETEXT, font_color=GREEN)
			selection = gm.run()
			if selection==menu_items[0]:
				GAMESTATE='play'
				state=0
			if selection==menu_items[1]:
				pplayers +=1
				pplayers = pplayers%5
				nplayers=2+pplayers
			if selection==menu_items[2]:
				extrachips +=100
				extrachips = extrachips%1000
				chips0 = blinds[0]*20 + extrachips
			if selection==menu_items[3]:
				sys.exit()
		elif GAMESTATE == 'pausemenu':
			menu_items = ('Resume', 'Main Menu', 'Save Game', 'Quit')
			gm = click_menu.GameMenu(DISPLAYSURF, menu_items, bg_color=DARKERGREEN, 
				font=scriptpath+'/Fonts/Alien_League.ttf', font_size=LARGETEXT, font_color=GREEN,
				bg_alpha=100)
			selection = gm.run()
			if selection==menu_items[0]:
				GAMESTATE='play'
			if selection==menu_items[1]:
				GAMESTATE='menu'
			if selection==menu_items[2]:
				if game_state!=None:
					game_state.update_players()
				saveloadpkl.save_obj(game_state, 'saved_game', loc = scriptpath+'/../Data/SaveGames/')
			if selection==menu_items[3]:
				sys.exit()
		elif GAMESTATE=='play':
			"""
			In this section as much as possible of the gameplay will be derived from pokerpy.py
			- this is where the main logic of the game should be stored.
			The exceptions to this should only be the graphical elements of the game.
			"""

			"""TO REWRITE ALL OF THIS ONCE pokerpy.py IS COMPLETEISH"""
			#State=0 --> init game
			#State=1 --> deal
			#State=2 --> play, blind
			update_flag=False
			if state==0:
				game_state=None
			poker_game = gameplay.PokerGame(DISPLAYSURF, [], textfontObj, bg_color=DARKERGREEN)

			game_state, action = poker_game.run(state, nplayers,chips0, blinds,mindiff, gstate=game_state)

			GAMESTATE =action


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
