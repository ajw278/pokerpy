from __future__ import print_function
import random
import numpy as np
import sys
sys.path.insert(0, '../Odds/')
import probs
import time

"""
basic_AI
Place holder for AI routines. Totally random decision.
"""
class basic():
	def __init__(self):
		return None


	def make_decision(self,self_player, players, table):
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
fix_min
Place holder for AI routines. Always bets minimum but stays in.
"""
class fix_min():
	def __init__(self):
		return None

	def make_decision(self, self_player, players, table):
		minbet = np.amax(table.roundvals) - table.roundvals[self_player.order]
		return minbet
