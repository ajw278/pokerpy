# Calculator of poker probabilities

# For now, it still needs several changes. I did not how to get cards from a
# shuffled deck that is missing  the cards in the table or in my hand, so cards
# are being randomly generated, allowing for repeated cards. I will look into
# this soon. Also, because of this, final probabilities are independent of
# number of opponents.  
from __future__ import print_function
import numpy as np
import random
import sys
import hand
from collections import namedtuple
try:
	from collections import Counter
except:
	import backport_Counter
from operator import attrgetter
import time


Card = namedtuple("Card", ["value", "kind"])



#For now, repeated cards are allowed, I have to fix that
def win_random(deck, my_cards, table, num_opponents, wtype='wt'):
	my_hand=[]
	opp_hand = [] 
	new_table = list(table)

	random.shuffle(deck)
	table_togo = 5 - len(table)
	new_table+=list(deck[:table_togo])
	del deck[:table_togo]
	my_hand =list(new_table)+list(my_cards)
	my_score = hand.full_hand_best(my_hand)[1]

	#print('____\nTable: ', new_table)
	#print('My hand: ', my_hand)
	opp_score = 0
	for i in range(num_opponents):
		if opp_score>my_score:
			return False
		opp_hand =list(new_table)+list(deck[:2])
		del deck[:2]
		temp_score = hand.full_hand_best(opp_hand)[1]
		if temp_score > opp_score:
			opp_score = temp_score

	#print('Opp hand: ', opp_hand)
	#print('I win? ', my_score>opp_score)
	if wtype=='wt':
		return my_score >= opp_score
	elif wtype=='w':
		return my_score > opp_score
	else:
		print('Probability return not specified correctly.')
		sys.exit()

def prob(table, my_cards, num_opponents, tol, dcards=[], wtype='wt'):
	sigma = 1.; win =0; tot = 0; samples = []
	deck = hand.poker_deck()
	for card in list(my_cards)+list(table)+list(dcards):
		deck.remove(card)
	while sigma > tol:
		new_deck =list(deck)
		if win_random(new_deck, my_cards, table, num_opponents, wtype=wtype) == True:
			win+=1.
		tot+=1.
		p = win/tot
		samples.append(p)
		if tot%100 == 0 and tot>=800:
			sigma = np.std(np.asarray(samples))
			print('Total: ', tot, 'Prob:', p, 'Sigma:', sigma)

	return p

if __name__=="__main__":
	
	table = []#[Card(3,2), Card(6,1), Card(10,3)]
	my_cards = [Card(0,1), Card(5,2)]
	#table = [Card(random.randint(2,14), random.randint(1,4)) for i in range(3)]
	#my_cards = [Card(random.randint(2,14), random.randint(1,4)) for i in range(2)]
	print('table cards', table)
	print('my_cards', my_cards)
	start_time = time.time()
	probability = prob(table,my_cards,1,2.5e-2)
	print('Probability of winning =', probability , 'after', time.time() - start_time, 'seconds.')
