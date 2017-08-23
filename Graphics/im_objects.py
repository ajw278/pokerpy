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

import pygame
import load
from collections import namedtuple
import os
import menu
import click_menu

scriptpath = os.path.dirname(os.path.realpath(__file__))

#Graphics dictionary - for the names of the card files
KIND_DICT = {0: 'd', 1:'c',2:'h',3:'s'}
VALUE_DICT = {0: 2, 1: 3, 2: 4, 3: 5, 4:6, 5:7,6:8,7:9,8:10,9:'j', 10:'q',11:'k',12:'a'}

CW2H = 0.6

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

"""
class, table_card
Pygame sprite definition:
init()
function to initialise card at a specified position,
In: named tuple card, two dim tuple position, card dimension tuple,
boolean - true if face up
--> Initialise card graphical object
flip()
In: no args (self)
--> Flip the card - reveal if face down, hide otherwise
"""
class table_card(pygame.sprite.Sprite):

	def __init__(self, card, position, cdims, face):
		pygame.sprite.Sprite.__init__(self)
		self.value = card[0]
		self.kind = card[1]

		self.name = str(VALUE_DICT[self.value])+ str(KIND_DICT[self.kind])
		self.up = face
		if self.up:
			self.image, self.rect = load.load_img(self.name +'.jpg')
		else:
			self.image, self.rect = load.load_img('cback.jpg')

		self.image = pygame.transform.scale(self.image, (cdims[0],cdims[1]))
		self.rect = self.image.get_rect()
		self.rect.center = position	
	
	def flip(self):
		if not self.up:
			self.up=True
			self.image, self.rect = load.load_img(self.name +'.jpg')

		else:
			self.up = False
			self.image, self.rect = load.load_img('cback.jpg')


	def is_mouse_selection(self, (posx, posy)):
		if self.rect.collidepoint(posx, posy):
			return True
		return False


"""
class, player_box
Create a box image in which the player data and cards are displayed
"""
class player_box(object):
	def __init__(self, font, dims, player, ncards, ptype='std'):
		#dims - left, top, width, height
		vspace = 0.5
		self.type = ptype
		self.coords = dims
		self.rect = pygame.Rect(dims)
		self.margin = int(float(dims[2])/10.)
		self.font = font
		self.text =[self.font.render("Player: {0.ID}".format(player), 1, (0,0,0)),self.font.render("Chips: {0.bank}".format(player), 1, (0,0,0))]
		self.txtrct = []
		self.textloc = []
		shft_down = 0
		for itxt in range(len(self.text)):
			self.txtrct.append(self.text[itxt].get_rect())
			shft_down+=self.txtrct[itxt].height
			self.textloc.append((dims[0]+int(float(dims[2]-self.txtrct[itxt].width)/2.),dims[1]+int(itxt*1.1*self.txtrct[itxt].height)))
		self.cardpos = []
		cwdth = int(float(dims[2]*0.9-2*self.margin)/float(ncards))
		self.csize = (cwdth, min(int(float(cwdth)/CW2H), int(vspace*dims[3])))
		for icard in range(ncards):
			px  = int((self.csize[0]*1.05)*icard+self.margin+self.csize[0]/2.)
			py = int((0.9-vspace)*dims[3]+shft_down)
			self.cardpos.append((px,py))
		self.cards = []


		self.turn = False
		

	def turn_on(self):
		self.turn =True
	
	def turn_off(self):
		self.turn = False


	def update(self, player):
		self.text =[self.font.render("Player: {0.ID}".format(player), 1, (0,0,0)),self.font.render("Chips: {0.bank}".format(player), 1, (0,0,0))]
		self.cards=[]
		for icard in range(len(player.hand)):
			px = self.cardpos[icard][0]
			py = self.cardpos[icard][1]
			position = (int(px+self.coords[0]), int(py+self.coords[1]))
			self.cards.append(table_card(player.hand[icard], position, self.csize, player.show))

	
	def is_mouse_selection(self, (posx, posy)):
		if self.rect.collidepoint(posx, posy):
			return True
		return False


	def set_mouse_selection(self, mpos, screen):
		"""Marks the MenuItem the mouse cursor hovers on."""

		s = pygame.Surface((self.coords[2],self.coords[3]))
		s.fill(GREEN)  # the size of your rect
		s.set_alpha(100)
		screen.blit(s, (self.coords[0],self.coords[1]))
		
		s.set_alpha(50)       # alpha level

		print('Checking: ', mpos)

		if self.is_mouse_selection(mpos):
			s.fill((0,255,0))
		else:
			if self.turn:
				s.fill((255,0,0))
			else:
				s.fill((0,0,0))

		
		screen.blit(s, (self.coords[0],self.coords[1]))

		for card in self.cards:
			screen.blit(card.image, card.rect)
		for itxt in range(len(self.text)):
			screen.blit(self.text[itxt], self.textloc[itxt])



	def response(self, screen):

		if self.type == 'std':
			if self.turn:
				menu_items = ['Manual Bet', 'Assign Cards', 'Suggest AI Move', 'Cancel']
			else:
				menu_items = ['Manual Bet', 'Assign Cards', 'Suggest AI Move', 'Cancel']
		else:
			print('Error: Player type not recognised.')
			sys.exit()

		ipm = click_menu.MiniGameMenu(screen, menu_items, bg_color=BLACK, bg_alpha=50, font=scriptpath+'/Fonts/Alien_League.ttf', font_size=30, font_color=WHITE, loc= (self.coords[0]-0.2*self.coords[2], self.coords[1]-0.1*self.coords[3]), size=(1.4*self.coords[2], 1.2*self.coords[3]))
		
		selection = ipm.run()

		if self.type=='std':
			if selection == menu_items[-1]:
				return 'resume'
			elif selection == menu_items[0]:
				print('Manual bet selected... Not implemented yet.')
				return 'resume'
			elif selection == menu_items[1]:
				print('Assign cards selected... Not implemented yet.')
				return 'resume'
			elif selection == menu_items[2]:
				print('Suggest AI move selected... Not implemented yet.')
				return 'resume'
		
		
			
"""
class, stats_box
"""
class stats_box(object):
	def __init__(self, font, dims, text):
		#dims - left, top, width, height
		vspace = 0.5
		self.coords = dims
		self.rect = pygame.Rect(dims)
		self.margin = int(float(dims[2])/10.)
		self.font = font
		self.text =text
		self.txtrct = []
		self.textloc = []
		shft_down = 0
		for itxt in range(len(self.text)):
			self.txtrct.append(self.text[itxt].get_rect())
			shft_down+=self.txtrct[itxt].height
			self.textloc.append((dims[0]+int(float(dims[2]-self.txtrct[itxt].width)/2.),dims[1]+int(itxt*1.1*self.txtrct[itxt].height)))
		

	def update(self, text):
		self.text = text

	def is_mouse_selection(self, (posx, posy)):
		if self.rect.collidepoint(posx, posy):
			return True
		return False


	def set_mouse_selection(self, mpos, screen):
		"""Marks the MenuItem the mouse cursor hovers on."""

		s = pygame.Surface((self.coords[2],self.coords[3]))  # the size of your rect
		s.set_alpha(100)       # alpha level

		if self.is_mouse_selection(mpos):

			s.fill((0,255,0))
		else:
			s.fill((0,0,0))
		
		screen.blit(s)
		


"""
class, player_box
Create a box image in which the player data and cards are displayed
"""
class dealer_box(object):
	def __init__(self,font, dims, ncards, csize):
		#dims - left, top, width, height
		vspace = 0.5
		self.coords= dims
		self.rect = pygame.Rect(dims)
		self.margin = dims[2]/10
		cardpos = []
		self.csize = csize
		for icard in range(ncards):
			cardpos.append(((self.csize[0]*1.05)*icard+self.margin,self.csize[1]/3.))
		self.ccoords = cardpos
		self.font =font
		self.text = [self.font.render("", 1, (0,0,0))]
		self.textloc = (dims[0],dims[1])
		self.txtrct = []
		self.textloc = []
		shft_down = 0
		for itxt in range(len(self.text)):
			self.txtrct.append(self.text[itxt].get_rect())
			shft_down+=self.txtrct[itxt].height
			self.textloc.append((dims[0]+int(float(dims[2]-self.txtrct[itxt].width)/2.),dims[1]+int(itxt*1.1*self.txtrct[itxt].height)))
		self.cards = []
		self.cardpos = []
		for icard in range(ncards):
			px  = int((self.csize[0]*1.05)*icard+self.margin+self.csize[0]/2.)
			py = int((0.9-vspace)*dims[3]+shft_down)
			self.cardpos.append((px,py))

	def update(self, table):
		if table.pot>0:
			self.text = [self.font.render("Pot: {0.pot}".format(table), 1, (0,0,0))]
		else:
			self.text = [self.font.render("", 1, (0,0,0))]
		self.cards=[]
		for icard in range(len(table.hand)):
			print(self.cardpos, icard)
			print(table.hand)
			pc = self.cardpos[icard]
			ps = self.coords
			position = (int(pc[0]+ps[0]), int(pc[1]+ps[1]))
			self.cards.append(table_card(table.hand[icard], position, self.csize, True))

	def is_mouse_selection(self, (posx, posy)):
		print(posx, posy)
		
		if self.rect.collidepoint(posx, posy):
			return True
		return False


	def set_mouse_selection(self, mpos, screen):
		"""Marks the MenuItem the mouse cursor hovers on."""

		s = pygame.Surface((self.coords[2],self.coords[3]))
		s.fill(GREEN)  # the size of your rect
		s.set_alpha(100)
		screen.blit(s, (self.coords[0],self.coords[1]))
		
		s.set_alpha(50)       # alpha level

		if self.is_mouse_selection(mpos):
			s.fill((0,255,0))
		else:
			s.fill((0,0,0))

		
		screen.blit(s, (self.coords[0],self.coords[1]))

		for card in self.cards:
			screen.blit(card.image, card.rect)
		for itxt in range(len(self.text)):
			screen.blit(self.text[itxt], self.textloc[itxt])

	def response(self, screen):

		if len(self.cards) == 0:
			menu_items = ['Manual Flop', 'Auto Flop', 'Player Order', 'Dealer', 'Cancel']
		elif len(self.cards)==3:
			menu_items = ['Manual Turn', 'Auto Turn', 'Player Order', 'Dealer', 'Cancel']
		elif len(self.cards)==4:
			menu_items = ['Manual River', 'Auto River', 'Player Order', 'Dealer', 'Cancel']
			
		else:
			menu_items = ['Manual Bet', 'Assign Cards', 'Player Order', 'Dealer', 'Cancel']

		ipm = click_menu.MiniGameMenu(screen, menu_items, bg_color=BLACK, bg_alpha=50, font=scriptpath+'/Fonts/Alien_League.ttf', font_size=30, font_color=WHITE, loc= (self.coords[0]-0.2*self.coords[2], self.coords[1]-0.1*self.coords[3]), size=(1.4*self.coords[2], 1.2*self.coords[3]))
		
		selection = ipm.run()

		if len(self.cards) == 0:
			if selection == menu_items[-1]:
				return 'resume'
			elif selection == menu_items[0]:
				print('Manual bet selected... Not implemented yet.')
				return 'resume'
			elif selection == menu_items[1]:
				print('Assign cards selected... Not implemented yet.')
				return 'resume'
			elif selection == menu_items[2]:
				print('Suggest AI move selected... Not implemented yet.')
				return 'resume'
			return 'resume'
		else:
			if selection == menu_items[-1]:
				return 'resume'
			elif selection == menu_items[0]:
				print('Manual bet selected... Not implemented yet.')
				return 'resume'
			elif selection == menu_items[1]:
				print('Assign cards selected... Not implemented yet.')
				return 'resume'
			elif selection == menu_items[2]:
				print('Suggest AI move selected... Not implemented yet.')
				return 'resume'
			return 'resume'


class DealerButton(pygame.sprite.Sprite):
	def __init__(self, positions, ID, dims):
		pygame.sprite.Sprite.__init__(self)
		self.positions = positions
		self.image, self.rect = load.load_img('dealer_button.jpg')
		self.image = pygame.transform.scale(self.image, dims)
		self.rect = self.image.get_rect()
		self.rect.center = self.positions[ID]

	def move_button(self, ID):
		self.rect.center = self.positions[ID]
	

"""
position_boxes:
In: screen width, screen height, no. cards per player, no. dealing cards, aiplayers, humanplayers, font
Out: card dimension (tuple), human player cards positions (list of tuples),
AI player cards positions (list of lists of tuples)
"""
def position_boxes(scw, sch, cardspp, dcards, aiplayers, humanplayers, font, dealID):
	nplayers = len(aiplayers)+len(humanplayers)
	nhumans = len(humanplayers)

	AI_boxes = []
	player_boxes = []
	margin =0.05
	scale = min((1.0-margin)/float(nplayers-nhumans), 0.2)
	boxdims = (scale, 0.25)
	left0ai = 0.5-boxdims[0]*(1.+(nplayers-nhumans-1))/2.
	left0h = 0.5-boxdims[0]*(1.+nhumans-1)/2.
	button_dim = (int(0.05*sch),int(0.05*sch))
	button_array = []
	AIy = margin

	Hy = 1.-boxdims[1]-margin
	for ibox in range(nhumans):
		Hx = 1.05*(boxdims[0]*ibox) +margin/2. +left0h
		dims = (Hx*scw, Hy*sch,boxdims[0]*scw, boxdims[1]*sch)
		player_boxes.append(player_box(font, dims, humanplayers[ibox], cardspp))
		csize = player_boxes[ibox].csize
		button_array.append((Hx*scw,(Hy+0.05*boxdims[1])*sch))

	for ibox in range(nplayers-nhumans):
		AIx = 1.05*(boxdims[0]*ibox)+margin/2.+left0ai
		dims = (AIx*scw, AIy*sch,boxdims[0]*scw, boxdims[1]*sch)
		AI_boxes.append(player_box(font, dims, aiplayers[ibox], cardspp))

		button_array.append((AIx*scw,(AIy+0.95*boxdims[1])*sch))
	

	deal_dims = (0.25*scw, 3.*sch/8., 0.5*scw, 0.25*sch)

	dealerbox = dealer_box(font, deal_dims, dcards, csize)

	button = DealerButton(button_array, dealID,button_dim)


	return player_boxes, AI_boxes, dealerbox, button


