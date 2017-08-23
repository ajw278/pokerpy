import numpy as np
cimport numpy as np
import sys
import random
import hand
from collections import namedtuple
try:
	from collections import Counter
except:
	import backport_Counter

#For now, repeated cards are allowed, I have to fix that
def win_random(list deck, list my_cards, list table,  str wtype='wt'):
	cdef int table_togo, my_score, opp_score
	cdef list new_table
	cdef list my_hand
	cdef list opp_hand 
	new_table = list(table)

	random.shuffle(deck)
	table_togo = 5 - len(table)
	new_table+=list(deck[:table_togo])
	del deck[:table_togo]
	my_hand =list(new_table)+list(my_cards)
	my_score = hand.full_hand_best(my_hand)[1]

	opp_hand =list(new_table)+list(deck[:2])
	del deck[:2]
	opp_score = hand.full_hand_best(opp_hand)[1]

	if wtype=='wt':
		return my_score >= opp_score
	elif wtype=='w':
		return my_score > opp_score
	else:
		print 'Probability return not specified correctly.'
		sys.exit()

def prob(list table, list my_cards, int ntrials, str wtype='wt', list dcards=[]):
	cdef list deck, new_deck, delete
	deck = hand.poker_deck()
	results = np.zeros(ntrials)
	delete = list(my_cards)+list(table)+list(dcards)
	for card in delete:
		deck.remove(card)
	for irun in range(ntrials):
		new_deck =list(deck)
		results[irun] = int(win_random(new_deck, my_cards, table, wtype=wtype))
	return np.mean(results)
