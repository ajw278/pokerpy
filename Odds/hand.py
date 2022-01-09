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


#hand.py 
#Hand definitions: useful functions for hand definition and analysis

from __future__ import print_function
from __future__ import division
from collections import namedtuple
try:
	from collections import Counter
except:
	from backport_Counter import Counter
import random
import numpy as np
import itertools

CARDS_PER_HAND = 5
VALUES = 13
KINDS = 4

Card = namedtuple("Card", ["value", "kind"])

"""
all_equal:
In: list of values
Out: true if all equal, false otherwise
"""
def all_equal(lst):
	return len(set(lst)) <= 1

"""
couples:
In: list of values
Out: sequential pairs of values
"""
def couples(lst):
	return [ [curr, lst[index + 1]] for index, curr in enumerate(lst[:-1])]


"""
one_by_one_increasing
In: list of values
Out: true if sequential, false otherwise
"""
def one_by_one_increasing(lst):
	return all(next == previous + 1 for previous, next in couples(lst))

"""
most_common:
In: list of values
Out: most common value in list
"""
def most_common(lst):
	if len(list(lst))>0:
		return Counter(lst).most_common()[0][0]
	else:
		return None

"""
most_common_count:
In: list of values
Out: number of times the most common entry occurs in list
"""
def most_common_count(lst):
	return lst.count(most_common(lst))

"""
first_true:
In: function argument, list of functions
Out: first function which returns true
"""
def first_true(arg, funcs):
	for f in funcs:
		if f(arg):
			return f

"""
values:
In: list of named tuples 'cards'
Out: card values
"""
def values(cards):
	return list([c.value for c in cards])

"""
kinds:
In: list of named tuples 'cards'
Out: suit values
"""
def kinds(cards):
	return [c.kind for c in cards]

def is_straight_flush(hand):
	return is_flush(hand) and is_straight(hand)

def is_flush(hand):
	return all_equal(kinds(hand))

def is_four_of_a_kind(hand):
	return most_common_count(values(hand)) == 4

def is_three_of_a_kind(hand):
	return most_common_count(values(hand)) == 3

def is_pair(hand):
	return most_common_count(values(hand)) == 2

def is_nothing(hand):
	return True

"""
is_straight:
In: hand
Out: True if contains straight, otherwise false
"""
def is_straight(hand):
	return one_by_one_increasing(sorted(values(hand)))

"""
is_two_pair:
In: hand
Out: True if contains two pair, otherwise false
"""
def is_two_pair(hand):
	return is_pair(hand) and is_pair([c for c in hand if c.value != most_common(values(hand))])


"""
is_full_house:
In: hand
Out: True if full house, otherwise false
"""
def is_full_house(hand):
	return is_three_of_a_kind(hand) and is_pair([c for c in hand if c.value != most_common(hand).value])

"""
poker_value:
In: Hand definition as 'card', list of functions defining hands from greatest to worst hand
Out: Highest hand value
"""
def poker_hand(hand, possible_scores=[is_straight_flush, is_four_of_a_kind, is_full_house,
                        is_flush, is_straight, is_three_of_a_kind, is_two_pair, is_pair, is_nothing]):
	return first_true(hand, possible_scores).__name__[3:]


"""
hand_value
Perhaps dodgy way to assign value to card hand
Bodged for now.
In: Hand
Out: value assigned to each hand - use suit vals??
"""
def hand_value(hand, suit_vals=False):
	hand_dict = {'nothing': 0, 'pair': 1, 'two_pair':2, 'three_of_a_kind': 3,  \
	'straight':4, 'flush': 5, 'full_house': 6, 'four_of_a_kind':7, 'straight_flush':8}

	valarray = np.zeros(len(hand)+1, dtype=int)
	
	hand_name = poker_hand(hand)
	valarray[0] =  hand_dict[hand_name]
	
	c_values = list(values(hand))
	ival = 1
	while (ival<len(valarray)-1) and len(list(c_values))>=1:
		c_values = list(c_values)
		mcommon_value = most_common(c_values)
		mcommon_count = list(c_values).count(mcommon_value)
		highest_mcommon=0
		val = 0
		for val in range(VALUES):
			if c_values.count(val)==mcommon_count:
				highest_mcommon = val

		c_values = filter(lambda a: a != highest_mcommon, c_values)
		valarray[ival] = highest_mcommon
		ival+=1

	value=0.0
	subtract = 0
	for ival in valarray:
		value += ival*(VALUES)**(len(hand)-subtract)
		subtract+=1	
	
	if suit_vals:
		print('Not set up for suit evaulation. Easy fix.')
		sys.exit()
	
	return value

def tiebreaker(hand):
	valarray = np.zeros(2, dtype=int)

	c_values = np.asarray(values(hand))
	c_kinds = np.asarray(kinds(hand))
	print(hand)
	print(values(hand))
	print(c_values, c_kinds)
	max_val = np.amax(c_values)
	bool_array = c_values==max_val
	cmax=0
	for ind in range(len(c_values)):
		if bool_array[ind]:
			if c_kinds[ind]>=cmax:
				max_ind =ind

	print('Tie break biggest card: ', hand[max_ind])
	print('From total hand: ', hand)

	valarray[0] = c_values[max_ind]
	valarray[1] = c_kinds[max_ind]

	print('Check: ', c_values[max_ind], c_kinds[max_ind])
	

	value=0.0
	value += valarray[0]*(VALUES)
	value += valarray[1]
	
	return value


"""
full_hand_best
In: larger hand, max number of cards in hand
Out: best hand, value of best hand
"""
def full_hand_best(full_hand, hand_size=CARDS_PER_HAND):

	all_hands = list(itertools.combinations(full_hand,hand_size))
	all_values = np.zeros(len(all_hands))
	for ihand in range(len(all_hands)):
		all_values[ihand] = hand_value(all_hands[ihand])
	
	maxind = np.argmax(all_values)

	return all_hands[maxind], all_values[maxind]

"""
poker_deck:
In: number of values, number of suits
Out: list containing type 'card' named tuple for each element of deck
"""
def poker_deck(max_value=VALUES, number_of_kinds=KINDS):
	deck=  [ Card(value, kind) for value in range(max_value) for kind in range(number_of_kinds)]
	return deck
