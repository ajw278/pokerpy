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
from collections import namedtuple

import sys
sys.path.insert(0, '../Odds/')
sys.path.insert(0, '../')
import im_objects
import hand
import pokerpy
import random

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

	settings_menu = menu.cMenu(SCW/5, 2*SCH/7, 20, 5, 'vertical', 100, DISPLAYSURF,
	       [('Play', 1, None),
		('Number Players', 2, None),
		('Starting Chips', 3, None),
		('Exit',       4, None)], TRANSP, LARGETEXT-5)

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

	#Load defaults would be done here - set them for now
	nplayers = 2
	pplayers = 0

	chips0 = 500
	extrachips=0

	while True:
		for e in pygame.event.get():
			if (e.type is pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
				pygame.display.toggle_fullscreen()

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
					state = 0 
					prev_state=1
					GAMESTATE='gamesetup'
				elif state == 2:
					state =0
				elif state ==3:
					state =0
				elif state ==4:
					state=0
				else:
					state=0
					terminate()

			# Quit if the user presses the exit button
			if e.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		elif GAMESTATE=='gamesetup':
			if prev_state != state:
				DISPLAYSURF.blit(mbg, (CENTER[0]-SCW/2,CENTER[1]-SCH/2))
				DISPLAYSURF.blit(titletextSurfaceObj, titletextRectObj)
				nplaytxt, nplayrect = textobj(str(nplayers), LARGETEXT-5, (4*SCW/5, 2*SCH/7 + 5+(LARGETEXT-5)))
				chipstxt, chipsrect = textobj(str(chips0), LARGETEXT-5, (4*SCW/5, 2*SCH/7 + 2*(5+(LARGETEXT-5))))
				pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key = 0))
				DISPLAYSURF.blit(nplaytxt,nplayrect)
				prev_state = state

			# Get the next event
			e = pygame.event.wait()

			# Update the menu, based on which "state" we are in 
			if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
				if state==0:
					rect_list, state = settings_menu.update(e, state)
				elif state == 1:
					state = 0 
					prev_state=1
					GAMESTATE='play'
				elif state == 2:
					pplayers +=1
					pplayers = pplayers%5
					nplayers=2+pplayers
					state=0
				elif state ==3:
					extrachips +=100
					extrachips = extrachips%1000
					chips0 = 500 + extrachips
					state =0
				elif state ==4:
					state=0
				else:
					terminate()

			# Quit if the user presses the exit button
			if e.type == pygame.QUIT:
				pygame.quit()
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
			if state==0:
				#Define the card dimensions and positions
				card_size, playerpos, AIpos, dealer_coords = im_objects.positions(SCH, SCH, 2, nplayers)
				print(playerpos, AIpos)
				#Define the initial dealer
				dealer = random.randint(0, nplayers-1)

				#Assign players to list
				players = []
				for iplayer in range(nplayers):
					if iplayer == 0:
						players.append(im_objects.player(chips0, iplayer, None))
					else:
						players.append(im_objects.player(chips0, iplayer, 'basic'))
				state=1

			if state==1:
				DISPLAYSURF.blit(mbg, (CENTER[0]-SCW/2,CENTER[1]-SCH/2))
				deck = hand.poker_deck()
				random.shuffle(deck)
				cardset, deck = pokerpy.init_deal(deck, nplayers, mode='texas', burn=True)
				iAI = 0
				cards_dict={}
				cards_sprites = {}
				for iplayer in range(nplayers):
					cards_dict[iplayer] = []
					if players[iplayer].ai == None:
						icard = 0
						for card in cardset[(dealer+iplayer)%nplayers]:
							cards_dict[iplayer].append(im_objects.table_card(card, playerpos[icard], card_size, True))	
							icard+=1
					else:
						icard = 0
						for card in cardset[(dealer+iplayer)%nplayers]:
							print(AIpos[iAI][icard], iAI, icard)
							cards_dict[iplayer].append(im_objects.table_card(card, AIpos[iAI][icard], card_size, False))
							icard+=1
						iAI+=1
					cards_sprites[iplayer] = []
					for ihand in range(len(cards_dict[iplayer])):
						cards_sprites[iplayer].append(pygame.sprite.RenderPlain(cards_dict[iplayer][ihand]))
						cards_sprites[iplayer][ihand].draw(DISPLAYSURF)	
				state=2
					


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
