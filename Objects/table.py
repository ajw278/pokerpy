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
"""
class poker_table:
	def __init__(self, nplayers):
		self.pot = 0
		self.invals = np.zeros(nplayers, dtype=int)
	
	def bid(self,value, player_id):
		self.invals[player_id] += value
		self.pot = int(np.sum(self.invals))

	#Define payout routine here.. unsure exactly
	#Have currently defined this to be pay to the
	#winner everything that they have put in from
	#each player, and return the rest to the original player
	def payout(self, winner_id):
		payout = 0
		paybacks = np.zeros(len(self.invals))
		for ipay in range(len(payouts)):
			payout += min(self.invals[ipay], self.invals[winner_id])
			paybacks[ipay] = max(self.invals[ipay]-self.invals[winner_id],0)
		self.pot = 0

		return payout, paybacks
