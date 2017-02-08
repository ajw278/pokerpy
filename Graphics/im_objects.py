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

#Graphics dictionary - for the names of the card files
KIND_DICT = {0: 'd', 1:'c',2:'h',3:'s'}
VALUE_DICT = {0: 2, 1: 3, 2: 4, 3: 5, 4:6, 5:7,6:8,7:9,8:10,9:'j', 10:'q',11:'k',12:'a'}

CW2H = 0.6

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


"""
class, player_box
Create a box image in which the player data and cards are displayed
"""
class player_box(object):
	def __init__(self, font, dims, player, ncards):
		#dims - left, top, width, height
		vspace = 0.5
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
		


	def update(self, player):
		self.text =[self.font.render("Player: {0.ID}".format(player), 1, (0,0,0)),self.font.render("Chips: {0.bank}".format(player), 1, (0,0,0))]
		self.cards=[]
		for icard in range(len(player.hand)):
			position = (int(self.cardpos[icard][0]+self.coords[0]), int(self.cardpos[icard][1]+self.coords[1]))
			self.cards.append(table_card(player.hand[icard], position, self.csize, player.show))

		


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
			position = (int(self.cardpos[icard][0]+self.coords[0]), int(self.cardpos[icard][1]+self.coords[1]))
			self.cards.append(table_card(table.hand[icard], position, self.csize, True))

"""
position_boxes:
In: screen width, screen height, no. cards per player, no. dealing cards, aiplayers, humanplayers, font
Out: card dimension (tuple), human player cards positions (list of tuples),
AI player cards positions (list of lists of tuples)
"""
def position_boxes(scw, sch, cardspp, dcards, aiplayers, humanplayers, font):
	nplayers = len(aiplayers)+len(humanplayers)
	nhumans = len(humanplayers)

	AI_boxes = []
	player_boxes = []
	margin =0.05
	scale = min((1.0-margin)/float(nplayers-nhumans), 0.2)
	boxdims = (scale, 0.25)
	left0ai = 0.5-boxdims[0]*(1.+(nplayers-nhumans-1))/2.
	left0h = 0.5-boxdims[0]*(1.+nhumans-1)/2.
	AIy = margin
	for ibox in range(nplayers-nhumans):
		AIx = boxdims[0]*ibox+margin/2.+left0ai
		dims = (AIx*scw, AIy*sch,boxdims[0]*scw, boxdims[1]*sch)
		AI_boxes.append(player_box(font, dims, aiplayers[ibox], cardspp))
	

	Hy = 1.-boxdims[1]-margin
	for ibox in range(nhumans):
		Hx = boxdims[0]*ibox +margin/2. +left0h
		dims = (Hx*scw, Hy*sch,boxdims[0]*scw, boxdims[1]*sch)
		player_boxes.append(player_box(font, dims, humanplayers[ibox], cardspp))
		csize = player_boxes[ibox].csize

	deal_dims = (0.25*scw, 3.*sch/8., 0.5*scw, 0.25*sch)

	dealerbox = dealer_box(font, deal_dims, dcards, csize)

	return player_boxes, AI_boxes, dealerbox


