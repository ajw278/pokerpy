from __future__ import print_function

import numpy as np
from collections import namedtuple
import copy

KINDS=4
VALUES=13


Card = namedtuple("Card", ["value", "kind"])

def permutate_map(ref):
	minsuit=KINDS-1
	for card in ref:
		if card.kind<minsuit:
			minsuit=card.kind

	return lambda i: (i-minsuit)%KINDS

#ID array - odds kwarg sorts the table values for efficiency.
def table2arr(ohand, otable, odds=True):
	hand = sorted(ohand, key=lambda x: x.value, reverse=True)
	if odds:
		table = sorted(otable, key=lambda x: x.value, reverse=True)

	pmap = permutate_map(hand)


	harray = -1.*np.ones(2*2)
	tarray = -1.*np.ones(5*2)

	for icard in range(len(hand)):
		harray[icard*2] = hand[icard].value
		harray[icard*2+1] = pmap(hand[icard].kind)

	for icard in range(len(table)):
		tarray[icard*2] = table[icard].value
		tarray[icard*2+1] = pmap(table[icard].kind)

	return np.append(harray, tarray)

def arr2table(arr):
	
	hand = []
	for icard in range(2):
		if arr[icard*2]>=0.:
			hand.append(Card(int(arr[icard*2]), int(arr[icard*2+1])))

	table = []
	
	for icard in range(5):
		if arr[icard*2+4]>=0.:
			table.append(Card(int(arr[icard*2+4]), int(arr[icard*2+5])))

	return hand, table

	


if __name__ =='__main__':
	print('Running test..')
	
	hands = []

	deck = [ Card(value, kind) for value in range(VALUES) for kind in range(KINDS)]

	example_hand = [Card(0,2),Card(1,2)]

	example_table = [Card(5,2)] #,Card(8,0), Card(8,1)]

	print('Hand in: ', example_hand, example_table)

	ID = table2arr(example_hand, example_table)
	print(ID)
	print(arr2table(ID))
	exit()
	


	IDs = []
	for card1 in deck:
		newdeck = copy.copy(deck)
		newdeck.remove(card1)
		for card2 in newdeck:
			hands.append([card1, card2])
			newdeck.remove(card2)
			for card3 in newdeck:
				nnewdeck = copy.copy(newdeck)
				nnewdeck.remove(card3)
				for card4 in nnewdeck:
					nnewdeck.remove(card4)
					for card5 in nnewdeck:
						newID = table2arr([card1, card2],[card3,card4,card5])
						if not any((newID == x).all() for x in IDs):
							IDs.append(newID)

				print('Collated {1} IDs for {0} hands..'.format(len(hands), len(IDs)))



	print('Number of hands: ', len(hands))
	print('Number of IDs:', len(IDs))




	
