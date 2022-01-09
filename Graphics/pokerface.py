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
sys.path.insert(0, '../AI/')
import ai_scripts
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

def create_playerdict(nplayers, chips0, gametype):
	defname_ = 'Player {0}'
	pldict  = {}
	
	for ipl in range(nplayers):
		if ipl==0:
			AI_type=None
			ptype = 'faceup'
		else:
			AI_type='fix_min'
			ptype = 'facedown'
		pldict[defname_.format(ipl)] = player.player(chips0, ipl, AI_type, defname_.format(ipl), ptype=ptype, gtype=gametype)

	return pldict


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
	DISPLAYSURF = pygame.display.set_mode((SCH, SCH)) # pygame.FULLSCREEN, 32)
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
	SMALLTEXT = int(SCH/30)
	MIDTEXT = int(SCH/25)
	LARGETEXT = int(SCH/15)
	MASSIVETEXT = int(SCH/8)
	titlefontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', int(LARGETEXT))
	levelfontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', int(MIDTEXT))
	textfontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', int(SMALLTEXT))

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

	all_types = ['auto', 'manual']
	itype = 0
	gametype=all_types[itype]
	chips0 = 400
	mindiff=5
	extrachips=0

	blinds = [10, 20]


	while True:
		for e in pygame.event.get():
			if (e.type is pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
				pygame.display.toggle_fullscreen()

		if GAMESTATE == 'menu':
			#Give an AI option
			play_ = 'Quick Start'
			set_ = 'Game Setup'
			aitest_ = 'AI Lab'
			load_ = 'Load'
			quit_ = 'Quit'

			menu_items = (play_, set_, load_, quit_)
			gm = click_menu.GameMenu(DISPLAYSURF, menu_items, bg_color=DARKERGREEN, 
				font=scriptpath+'/Fonts/Alien_League.ttf', font_size=LARGETEXT, font_color=GREEN)
			selection = gm.run()
			if selection==play_:
				GAMESTATE='play'
				pldict = create_playerdict(nplayers, chips0, gametype)
			if selection==set_:
				GAMESTATE='gamesetup'
			if selection==load_:
				pldict = create_playerdict(nplayers, chips0, gametype)
				try:
					game_state = saveloadpkl.load_obj('saved_game',loc=scriptpath+'/../Data/SaveGames/')
					state = game_state.state
					GAMESTATE='play'
				except:
					print('No save data found.')
					GAMESTATE='menu'
			if selection==quit_:
				sys.exit()
		elif GAMESTATE=='gamesetup':
			#Change these items to give a 'game settings' option
			play_ = 'Play'
			gtype_ = 'Game Type: {0}'.format(gametype)
			players_ = 'Players: {0}'.format(nplayers)
			startchip_ = 'Starting Chips: {0}'.format(chips0)
			quit_ = 'Quit'
			menu_items = (play_,players_, startchip_, gtype_, quit_ )
			gm = click_menu.GameMenu(DISPLAYSURF, menu_items, bg_color=DARKERGREEN, 
				font=scriptpath+'/Fonts/Alien_League.ttf', font_size=LARGETEXT, font_color=GREEN)
			selection = gm.run()
			if selection==play_:
				GAMESTATE='player_set'
				pldict = create_playerdict(nplayers, chips0, gametype)
				state=0
			if selection==gtype_:
				itype +=1
				itype = itype%len(all_types)
				gametype = all_types[itype]
			if selection==players_:
				pplayers +=1
				pplayers = pplayers%5
				nplayers=2+pplayers
			if selection==startchip_:
				extrachips +=100
				extrachips = extrachips%1000
				chips0 = blinds[0]*20 + extrachips
			if selection==quit_:
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

		elif GAMESTATE=='player_set':
			start_ = 'Start'

			menu_items = [start_]
			pl_items = []
			for playerkey in pldict:
				pl_items.append('{0}'.format(playerkey))
				menu_items.append('{0}'.format(playerkey))
			menu_items = tuple(menu_items)

			gm = click_menu.GameMenu(DISPLAYSURF, menu_items, bg_color=DARKERGREEN, 
				font=scriptpath+'/Fonts/Alien_League.ttf', font_size=LARGETEXT, font_color=GREEN,
				bg_alpha=100)
			selection = gm.run()
			if selection==start_:
				GAMESTATE='play'
			if selection in pl_items:
				back_='Done'
				none_ = 'None'
				cancel_='Cancel'

				SUBSTATE=GAMESTATE
				while SUBSTATE==GAMESTATE:
					if pldict[selection].auto:
						AUTO = 'On'
					else:
						AUTO = 'Off'

					
					if pldict[selection].initdeal:
						IDEAL = 'On'
					else:
						IDEAL = 'Off'

					name_ = 'Name: {0}'.format(pldict[selection].name)
					ai_ = 'AI: {0}'.format(pldict[selection].ai_type)
					auto_ = 'Auto: {0}'.format(AUTO)
					initdeal_ = 'Initial Deal: {0}'.format(IDEAL)
					
					DISPLAYSURF.fill(DARKERGREEN)
					submenu_items = (name_, ai_,auto_,initdeal_, back_)

					
					sm_width= DISPLAYSURF.get_rect().width*0.3
					sm_height=DISPLAYSURF.get_rect().height*0.7
					sm_centerx = DISPLAYSURF.get_rect().centerx-sm_width/2.
					sm_centery = DISPLAYSURF.get_rect().centery-sm_height/2.
				
					submenu = click_menu.MiniGameMenu(DISPLAYSURF, submenu_items, bg_color=BLACK, bg_alpha=50, font=scriptpath+'/Fonts/Alien_League.ttf', font_size=30, font_color=WHITE, loc=(sm_centerx, sm_centery), size=(sm_width, sm_height))

					subselection = submenu.run()

					if subselection==back_:
						SUBSTATE=None
					if subselection==name_:
						fontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', 30)
						pname = click_menu.get_text(DISPLAYSURF, fontObj,prompt_string='Player name: ')
						pldict[selection].rename(pname)
						SUBSTATE=GAMESTATE
					if subselection==auto_:
						pldict[selection].set_auto()
					if subselection==initdeal_:
						pldict[selection].set_initdeal()
					if subselection==ai_:
						subsubmenu_items = [] 
						for a in dir(ai_scripts):
							if not a.startswith('__'):
								subattr = [b for b in dir(getattr(ai_scripts, a)) if (not b.startswith('__') and not b.startswith('func'))]
								if len(subattr)==0:
									subsubmenu_items.append(a)
								
						subsubmenu_items += [none_, cancel_]
						subsubmenu =  click_menu.MiniGameMenu(DISPLAYSURF, subsubmenu_items, bg_color=BLACK, bg_alpha=50, font=scriptpath+'/Fonts/Alien_League.ttf', font_size=30, font_color=WHITE, loc=(sm_centerx, sm_centery), size=(sm_width, sm_height))
						subsubselection = subsubmenu.run()

						if subsubselection==cancel_:
							SUBSTATE=GAMESTATE
						elif subsubselection==none_:
							pldict[selection].set_ai(None)
						else:
							pldict[selection].set_ai(subsubselection)
							
						
						
						
			
		elif GAMESTATE=='play':
			#State=0 --> init game
			#State=1 --> deal
			#State=2 --> play, blind
			update_flag=False
			if state==0:
				game_state=None
			poker_game = gameplay.PokerGame(DISPLAYSURF, [], textfontObj, bg_color=DARKERGREEN, game_type=gametype)

			action='resume'
			while action=='resume':
				game_state, action = poker_game.run(state, pldict,chips0, blinds,mindiff, gstate=game_state)
				state = game_state.state

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
