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

import numpy as np
"""
class poker_table
Not sure about how to divide up pot properly - check!
"""
class poker_table:
	def __init__(self, nplayers):
		self.hand = []
		self.nplayers = nplayers
		self.pot = 0
		self.invals = np.zeros(nplayers, dtype=int)
		self.roundvals = np.zeros(nplayers, dtype=int)

	def new_hand(self):
		self.pot = 0
		self.hand=[]
		self.invals = np.zeros(self.nplayers, dtype=int)
		self.roundvals = np.zeros(self.nplayers, dtype=int)

	def new_round(self):
		self.roundvals = np.zeros(self.nplayers, dtype=int)
	
	def bid(self,value, player_order):
		self.roundvals[player_order] += value
		self.invals[player_order] += value
		self.pot = int(np.sum(self.invals))

	def deal(self, cards):
		for card in cards:
			self.hand.append(card)

	#Define payout routine here.. unsure exactly
	#Have currently defined this to be pay to the
	#winner everything that they have put in from
	#each player, and return the rest to the original player
	def payout(self, winner_orders):
		nwinners = len(winner_orders)
		payout = 0
		payouts_in = np.zeros(len(self.invals))
		payouts_out = np.zeros(len(self.invals))
		payouts = np.zeros(len(self.invals))
		#Payouts defined as the payin of each winner divided by number of winners
		for ipay in range(len(payouts_in)):
			if ipay in winner_orders:
				for jpay in range(len(self.invals)):
					payouts_in[ipay] += min(self.invals[jpay], self.invals[ipay])/nwinners
					payouts_out[jpay] += min(self.invals[jpay], self.invals[ipay])/nwinners

		for ipay in range(len(payouts_in)):
			payouts[ipay] = self.invals[ipay]- payouts_out[ipay]+payouts_in[ipay]
			
			
		return payouts

