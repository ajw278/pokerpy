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
#Poker game setup and play routine
from __future__ import print_function
import re
import random
import sys
sys.path.insert(0, './Odds/')
sys.path.insert(0, './Objects/')
sys.path.insert(0, './Data/')
import hand
import player
import table
import numpy as np


"""
get_defaults
In: defaults file name
Out: default values
"""
def read_defaults(defaults='defaults.dat'):
	try:
		f=open('Data/'+str(defaults))
		lines=f.readlines()
		f.close()
	except IOError:
		print("Missing defaults file: ", defaults)
		sys.exit()

	for line in lines:
		try:
			if 'NHUMAN' in line:
				NHUMAN = int(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
			elif 'NAI' in line:
				NAI = int(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
			elif 'VALUES' in line:
				VALUES = int(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
			elif 'KINDS' in line:
				KINDS = int(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
			elif 'SMALL_BLIND' in line:
				SMALL_BLIND = int(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
			elif 'BIG_BLIND' in line:
				BIG_BLIND = int(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
			elif 'CHIPS0' in line:
				CHIPS0 = int(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
		except ValueError:
			print('Error reading defaults.')
			sys.exit()

	try:
		return NHUMAN, NAI, VALUES, KINDS, SMALL_BLIND, BIG_BLIND, CHIPS0
	except ValueError:
		print('Not all variables defined in defaults file.')
		sys.exit()

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

"""
get_players
In: number human players, number ai players, start chips, (opt) player names
Out: Dictionary - key player names, entry player object
"""
def get_players(nhuman, nai, chips0, pnames=[]):
	
	players = {}
	iplyr_tot=0
	for iplyr in range(nhuman):
		if len(pnames)>iplyr_tot:
			players[pnames[iplyr_tot]] = player.player(chips0, iplyr_tot, None)
		else:
			players['Player '+str(iplyr_tot+1)] = player.player(chips0, iplyr_tot, None)
		iplyr_tot+=1

	for iplyr in range(nai):
		if len(pnames)>iplyr_tot:
			players[pnames[iplyr_tot]] = player.player(chips0, iplyr_tot, 'basic')
		else:
			players['Player '+str(iplyr_tot+1)] = player.player(chips0, iplyr_tot, 'basic')
		iplyr_tot+=1

	return players

"""
init_deck
In: None
Out: shuffled deck - list of named tuples 'card' defined in hand module
"""
def init_deck():
	deck = hand.poker_deck()
	random.shuffle(deck)
	return deck

"""
init_dealer
In: Number of players
Out: Random index of starting dealer
"""
def init_dealer(nplayers):
	dealer = random.randint(0, nplayers-1)
	return dealer

"""
assign_hand
In: dealer index, player dictionary, hand list
Out: player dictionary with hands assigned
"""
def assign_hand(dealer, players, hands):
	nplayers = len(players)
	hands_all = range(len(hands))
	for plyr_key in players:
		for hand_no in hands_all:
			if players[plyr_key].order==(dealer+hand_no+1)%nplayers:
				players[plyr_key].deal_cards(hands[hand_no])
				print(dealer, plyr_key, hand_no, hands[hand_no], '\n**********\n')
		
	
	return players


"""
play_hand
In: small blind, big blind, player dictionary, dealer index, exit signal
"""
def play_hand(sblind, bblind, players, dealer, exit):
	DECK = init_deck()
	NPLAYERS = len(players)
	HANDS, DECK = init_deal(DECK, NPLAYERS)
	players  = assign_hand(dealer, players, HANDS)


	exit.append(True)
	return 0


def main():
	NHUMAN, NAI, VALUES, KINDS, SMALL_BLIND, BIG_BLIND, CHIPS0 = read_defaults()
	PLAYERS = get_players(NHUMAN, NAI, CHIPS0)
	NPLAYERS = NHUMAN + NAI
	TABLE = table.poker_table(NPLAYERS)
	DEALER = init_dealer(NPLAYERS)
	EXIT=[]
	while len(PLAYERS)>1 and not True in EXIT:
		play_hand(SMALL_BLIND, BIG_BLIND, PLAYERS, DEALER, EXIT)
		DEALER+=1
		DEALER = DEALER%NPLAYERS

	if True in EXIT:
		print('Exit signal received.')
		sys.exit()
	elif len(PLAYERS)==1:
		for key in PLAYERS:
			winner = key

		print('Winner: ', winner)
		print('Chips: ', PLAYERS[winner].bank)

	return 0


if __name__ == "__main__":
	main()
