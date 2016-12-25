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
import random
import numpy as np

"""
basic_AI
Place holder for AI routines. Totally random decision.
"""
def basic_AI(self_player, players, table):
	minbet = np.amax(table.roundvals) - table.roundvals[self_player.order]
	cointoss = random.randint(1, 3)
	if cointoss==1:
		return minbet+10
	elif cointoss==2:
		return minbet
	elif minbet>0:
		return 'f'
	else:
		return 0

"""
player class:
This is the generic class for all players, human or AI
It will need to updated as we understand how we're going to do this
My current thinking is that the AI will have access to a model in this class
i.e. a guess at how this player will play
as well as the number of chips and any other publically available information
"""
class player:
	
	def __init__(self, chips, num, AI_type):
		self.bank = chips
		#ID does not change, order changes as dealer changes
		self.ID = num
		self.order = num
		
		#Hand definition
		self.hand = []
		
		#If show is True, will allow AIs, humans to see hand
		self.show = False

		#Round status - betting for in and out of chips
		self.betting = True
		self.fold = False

		#Player type, to be updated with model by AI
		self.ptype = None

		#Define routine for AI.. not sure 
		#the best way to do this yet
		if AI_type == None:
			self.ai = None
		elif AI_type == 'basic':
			self.ai = basic_AI

	def new_round(self, num):
		self.order = num
		self.betting = True
		self.fold = False
		self.hand = []

	def show_hand(self):
		self.show = True

	def deal_cards(self, cards):
		for card in cards:
			self.hand.append(card)
	
	def spend(self, value):
		if self.bank>value:
			self.bank -= value
			return True
		elif self.bank==value:
			self.bank -= value
			self.betting = False
			return True
		else:
			return False			

	def win(self, value):
		self.bank += chips

	def choose_bet(self, players, table):
		if self.ai!=None:
			return self.ai(self, players, table)
		else:
			print('Bet error.')
			sys.exit()

	def hand_fold(self, show):
		self.betting = False
		self.fold = True
		self.show  = show
		
