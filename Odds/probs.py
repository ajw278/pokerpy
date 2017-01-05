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
from collections import namedtuple, Counter
from operator import attrgetter
import time

Card = namedtuple("Card", ["value", "kind"])

#For now, repeated cards are allowed, I have to fix that
def win_random(table, my_cards, num_opponents):
	deck = hand.poker_deck()
	for card in my_cards:
		deck.remove(card)
	for card in table:
		deck.remove(card)

	new_table = list(table)

	random.shuffle(deck)
	table_togo = 5 - len(table)
	if table_togo != 0:
		for i in range(table_togo):
			table_card = deck[0]
			new_table.append(table_card)
			deck.remove(table_card)
	my_hand =new_table+my_cards
	my_score = hand.full_hand_best(my_hand)[1]

	opp_score = 0
	for i in range(num_opponents):
		if opp_score>my_score:
			return False
		opp_hand =list(new_table)
		for i in range(2):
			opp_card = deck[0]
			deck.remove(opp_card)
			opp_hand.append(opp_card)
		temp_score = hand.full_hand_best(opp_hand)[1]
		if temp_score > opp_score:
			opp_score = temp_score

	return my_score > opp_score

def prob(table, my_cards, num_opponents, tol):
	sigma = 1.; win =0; tot = 0; samples = []
	while sigma > tol:
		if win_random(table, my_cards, num_opponents) == True:
			win+=1.
		tot+=1.
		p = win/tot
		samples.append(p)
		if tot%100 == 0 and tot>=1000:
			sigma = np.std(np.asarray(samples[len(samples)-100:]))
			print('Total: ', tot, 'Prob:', p, 'Sigma:', sigma)

	return p

if __name__=="__main__":
	
	table = []#[Card(3,2), Card(6,1), Card(10,3)]
	my_cards = [Card(12,1), Card(12,2)]
	#table = [Card(random.randint(2,14), random.randint(1,4)) for i in range(3)]
	#my_cards = [Card(random.randint(2,14), random.randint(1,4)) for i in range(2)]
	print('table cards', table)
	print('my_cards', my_cards)
	start_time = time.time()
	probability = prob(table,my_cards,9,1.e-2)
	print('Probability of winning =', probability , 'after', time.time() - start_time, 'seconds.')
