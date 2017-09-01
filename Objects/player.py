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
import sys
sys.path.insert(0, '../Odds/')
sys.path.insert(0, '../AI/')
import probs
import time
import ai_scripts


"""
player class:
This is the generic class for all players, human or AI
It will need to updated as we understand how we're going to do this
My current thinking is that the AI will have access to a model in this class
i.e. a guess at how this player will play
as well as the number of chips and any other publically available information
"""
class player:
	def __init__(self, chips, num, AI_type, name, ptype='facedown'):
		self.bank = chips
		#ID does not change, order changes as dealer changes
		self.ID = num
		self.name = name
		self.order = num
		self.ptype = ptype
		
		#Hand definition
		self.hand = []

		self.out=False
		
		#If show is True, will allow AIs, humans to see hand
		self.show = False
		self.auto = True
		if self.ptype=='faceup':
			self.show=True
			self.auto=False

		self.show0 = self.show
		self.turn=False

		#Round status - betting for in and out of chips
		self.betting = True
		self.fold = False

		self.set_ai(AI_type)

		#Define routine for AI.. not sure 
		#the best way to do this yet
		
	def rename(self, name):
		self.name =name


	def set_ai(self, AI_type):
		print('Setting ai:', AI_type)
		
		self.ai_type = AI_type
		
		if AI_type == None:
			self.ai = None
			self.auto=False
		else:
			ais_all = [a for a in dir(ai_scripts) if not a.startswith('__')]
			success=False
			for AI in ais_all:
				if AI==AI_type:
					self.ai = getattr(ai_scripts, AI)
					success=True
					break

			if not success:
				print('Error: could not locate AI: {0}'.format(AI_type))
				sys.exit()


	def set_auto(self):
		if self.ai!=None:
			self.auto = not self.auto
		else:
			self.auto = False

	def new_round(self, num=None):
		self.order = num
		if self.bank>0:
			self.betting = True
			self.out = False
			self.fold = False
		else:
			self.betting = False
			self.out = True
			self.fold = True
		self.hand = []
		self.show = self.show0

	def show_hand(self):
		self.show = True

	def deal_cards(self, cards):
		for card in cards:
			self.hand.append(card)
	
	def spend(self, value):
		self.turn=False
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
		self.bank += value
		if self.bank>0:
			self.betting=True
		else:
			self.betting=False

	def choose_bet(self, players, table):
		if self.ai!=None:
			return self.ai(self, players, table)
		else:
			print('Error: Asked for betting choice with no AI ({0})'.format(self.name))
			sys.exit()

	def hand_fold(self, show):
		self.betting = False
		self.fold = True
		self.show  = show
		self.turn = False

	def end_turn(self):
		self.turn=False

	def start_turn(self):
		self.turn=True

	def eliminate(self):
		self.betting=False
		self.out=True
		self.hand = []
		
