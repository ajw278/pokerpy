from __future__ import print_function

import pygame
import load
from collections import namedtuple

#Graphics dictionary - for the names of the card files
KIND_DICT = {0: 'd', 1:'c',2:'h',3:'s'}
VALUE_DICT = {0: 2, 1: 3, 2: 4, 3: 5, 4:6, 5:7,6:8,7:9,8:10,9:'j', 10:'q',11:'k',12:'a'}

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


def basic_AI(hand, table, chips, minbet):
	return max(10, minbet)


class player:
	
	def __init__(self, chips, num, AI_type):
		self.bank = chips
		self.order = num
		if AI_type == None:
			self.ai = None
		elif AI_type == 'basic':
			self.ai = basic_AI

	def new_order(self, num):
		self.order = num

	def bet(hand, table, chips, minbet):
		if self.ai!=None:
			return self.ai(hand, table, chips)
		else:
			print('Bet error.')
			sys.exit()



	

"""
positions:
In: screen width, screen height, no. cards per player, no. total players
Out: card dimension (tuple), human player cards positions (list of tuples),
AI player cards positions (list of lists of tuples)
"""
#Something bizarre happening with coords... divided by +1..
def positions(scw, sch, cardspp, nplayers):
	NDEALER =5
	pad = 5
	mindim = min(scw,sch)
	card_dims = (mindim/10, mindim/6)

	
	dealer_coords = []
	for icard in range(NDEALER):
		dealer_coords.append((scw/2+(icard-NDEALER)*(pad+card_dims[0]) , sch/2))

	playerpos = []
	AIpos = []

	#Divide by +1 here and in AI
	xcenter= scw/3
	for icards in range(cardspp):
		playerpos.append((xcenter-(icards-cardspp)*(pad+card_dims[0]), sch-(pad+card_dims[1])))

	AIy = card_dims[1]+pad
	for iplayer in range(nplayers-1):
		AIpos.append([])
		xcenter = (iplayer+1)*scw/(nplayers+1)
		
		print(xcenter, iplayer, nplayers)
		print(xcenter, scw/2)
		for icards in range(cardspp):
			AIpos[iplayer].append((xcenter-(icards-cardspp)*(pad+card_dims[0]), AIy))
	
	return card_dims, playerpos, AIpos, dealer_coords

