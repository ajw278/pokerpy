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


#pokerpy.py 
#Poker game setup and rules definitions
from __future__ import print_function

import sys

"""
deal:
In: shuffled deck (list of tuples), number output cards, burn (True or False)
NOTE: currently burning after each deal - is this right?
Out: list of cards, shortened deck
"""
def deal(shuffled_deck, ncards, burn=True):
	out_cards = []

	for icard in range(ncards):
		if len(shuffled_deck)!=0:
			out_cards.append(shuffled_deck[0])
			del shuffled_deck[0]
			if burn:
				del shuffled_deck[0]
		else:
			print('Run out of cards error.')	
			sys.exit()

	return out_cards, shuffled_deck

"""
init_deal:
In: shuffled deck (list of tuples), number of players, burn (True or False)
Out: list of hands, reduced deck
"""
def init_deal(shuffled_deck, nplayers, mode='texas', burn=True):

	all_hands = []

	if mode=='texas':
		for iplayer in range(nplayers):
			cards, shuffled_deck = deal(shuffled_deck, 2, burn=burn)
			all_hands.append(cards)
	else:
		print('Mode not implemented.')
		sys.exit()

	return all_hands, shuffled_deck






