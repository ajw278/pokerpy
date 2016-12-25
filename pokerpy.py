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
import itertools


"""
LIST OF RULES TO ADD:
Head-to-head: small blind is the dealer, big blind is the other --> change in order
Game types: Texas Hold'em (No Limit, Limit, Pot Limit): texas(NL/L/PL), other types
Kinds: Include kind types at end?
Draw: Include routine if the same hand
"""

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
				NHUMAN = int(re.findall(r"[-+]?\d*\.\d+|\d+", line.split('=')[1])[0])
			elif 'NAI' in line:
				NAI = int(re.findall(r"[-+]?\d*\.\d+|\d+", line.split('=')[1])[0])
			elif 'VALUES' in line:
				VALUES = int(re.findall(r"[-+]?\d*\.\d+|\d+", line.split('=')[1])[0])
			elif 'KINDS' in line:
				KINDS = int(re.findall(r"[-+]?\d*\.\d+|\d+", line.split('=')[1])[0])
			elif 'SMALL_BLIND' in line:
				SMALL_BLIND = int(re.findall(r"[-+]?\d*\.\d+|\d+", line.split('=')[1])[0])
			elif 'BIG_BLIND' in line:
				BIG_BLIND = int(re.findall(r"[-+]?\d*\.\d+|\d+", line.split('=')[1])[0])
			elif 'CHIPS0' in line:
				CHIPS0 = int(re.findall(r"[-+]?\d*\.\d+|\d+", line.split('=')[1])[0])
			elif 'GAME' in line:
				GAME = str(line.split('=')[1]).strip()
		except ValueError:
			print('Error reading defaults.')
			sys.exit()

	try:
		return NHUMAN, NAI, VALUES, KINDS, SMALL_BLIND, BIG_BLIND, CHIPS0, GAME
	except ValueError:
		print('Not all variables defined in defaults file.')
		sys.exit()

"""
deal:
In: shuffled deck (list of tuples), number output cards, burn (True or False)
Out: list of cards, shortened deck
"""
def deal(shuffled_deck, ncards, burn=False):
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
In: shuffled deck (list of tuples), number of players
Out: list of hands, reduced deck
"""
def init_deal(shuffled_deck, nplayers, mode='texasNL'):

	all_hands = []

	if mode=='texasNL':
		for iplayer in range(nplayers):
			cards, shuffled_deck = deal(shuffled_deck, 2, burn=False)
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
		oorder = players[plyr_key].order
		players[plyr_key].new_round((oorder+dealer)%nplayers)
		for hand_no in hands_all:
			if players[plyr_key].order==(hand_no+1)%nplayers:
				players[plyr_key].deal_cards(hands[hand_no])

	return None


"""
get_bet
Take betting decision from command line
In: min bet, max bet, multiple of bet, players, key, table
"""
def get_bet(players,plyrkey, table,mindiff = 5, blind=None):
	minimum = np.amax(table.roundvals) - table.roundvals[players[plyrkey].order]
	maximum = players[plyrkey].bank

	bet = minimum-10
	while bet<minimum or bet>maximum or bet%mindiff!=0:
		print('("f" - fold, "F - fold and show hand,  "h" - see hand, "t" - show table hand)')
		bet = raw_input('Bet (in multiples %s) between %d and %d: ' %(mindiff, minimum, maximum))
		if bet=='h':
			print('Hand:', players[plyrkey].hand, '\nChips: %d' %(players[plyrkey].bank))
		elif bet =='t':
			print('Table: ', table.hand, '\nPot: %d' %(table.pot))
		elif bet=='f' or bet=='F':
			break

		try:
			bet = int(bet)
		except ValueError:
			pass

		if type(bet)!=int:
			bet=minimum-10

	return bet

"""
make_bet
In: player class object, table class object, bet value (f/F for fold hide/show)
Out: None
"""
def make_bet(player, table, bet):
	if type(bet)!=str:
		bet_check = player.spend(bet)
		err_flag = False
		i_flag=0
		while not bet_check and not err_flag:
			print('Bet too high for player. Betting all in...')
			bet_check = player.spend(player.bank)
			i_flag+=1
			if i_flag>2:
				err_flag=True
			
		if err_flag:
			print('Error in betting.')
			sys.exit()
		
		table.bid(bet, player.order)
	else:
		if bet=='f':
			player.hand_fold(False)
		elif bet=='F':
			player.hand_fold(True)
		else:
			print('Bet signal "%s" not recognised.'%bet)
			sys.exit()

	return None

"""
round
NOTE: Not sure how to end betting, how many rounds should be allowed
"""
def std_round(players, table, blinds, blind_round=False, game='texasNL'):
	sblind = min(blinds)
	bblind = max(blinds)
	nplayers = len(players)
	inplayers = nplayers
	table.new_round()
	bet=0
	new_bet=0
	current=0
	#Bodge job for ending rounds atm 
	RoundFlag=True
	RoundRecord = []
	iround =0
	if 'texasNL' in game:
		while RoundFlag: 
			print('Bet number: ', iround)
			inplayers = 0
			for plkey in players:
				if players[plkey].order==iround%nplayers and players[plkey].betting:
					plind = players[plkey].order
					if players[plkey].ai != None:
						print('AI player.')
					if blind_round:
						if iround==0:
							print('%s bets small blind: %d' %(plkey, sblind))
							new_bet=sblind
						elif iround==1:
							print('%s bets big blind: %d' %(plkey, bblind))
							new_bet=bblind
					if (not blind_round) or (not (iround==1 or iround==0)):
						if players[plkey].ai == None:
							new_bet = get_bet(players,plkey,table)
						else:
							new_bet = players[plkey].choose_bet(players, table)
					if new_bet>np.amax(table.roundvals):
						RoundRecord.append(players[plkey].ID)
					make_bet(players[plkey], table, new_bet)
					print('%s bets : '%plkey, new_bet, ' for a total of ', table.roundvals[plind], 'this round.')
				#the last player to take aggressive action by a bet or raise is the first to show the hand
				#hence we need a record of who has raised last in each round
				if not players[plkey].fold:
					round_val = np.amax(table.roundvals)
					inplayers+=1

			iround +=1
			if iround>nplayers:
				RoundFlag=False
				for plkey in players:
					if players[plkey].betting and table.roundvals[players[plkey].order]!=round_val:
						RoundFlag=True
						
			
			bet=new_bet
			new_bet='error'
			#Define here current min bet size
			print('Players remaining in this hand: ', inplayers)
	else:
		print('Game mode "%s" not implemented yet.' %game)

	return RoundRecord

"""
showdown
Convoluted and unecessarily complicated right now... need to check all this
In: Players, table, betting order (not used atm, for the reveal if needed)

"""
def showdown(players, table, betorder):
	print(betorder)
	playing_hands_name={}
	playing_hands = {}
	playing_values = {}
	max_hand_val =0
	for plkey in players:
		if not players[plkey].fold:
			tot_hand = players[plkey].hand + table.hand
			all_hands = list(itertools.combinations(tot_hand,5))
			all_values = np.zeros(len(all_hands))
			for ihand in range(len(all_hands)):
				all_values[ihand] = hand.hand_value(all_hands[ihand])
				
			maxind = np.argmax(all_values)
			playing_hands[plkey] = all_hands[maxind]
			playing_hands_name[plkey] = hand.poker_hand(all_hands[maxind])
			playing_values[plkey] = hand.hand_value(all_hands[maxind])
			
	for plkey in playing_hands:
		max_hand_val = max(max_hand_val, playing_values[plkey])

	win_inds = []

	for plkey in playing_hands:
		if playing_values[plkey]==max_hand_val:
			win_inds.append(players[plkey].order)

	
	payouts = table.payout(win_inds)
	
	for ipay in range(len(payouts)):
		for plkey in players:
			if players[plkey].order==ipay:
				players[plkey].win(payouts[ipay])
				print('\nWinnings for %s: %d'%(plkey, payouts[ipay]))
				print('Hand: ', players[plkey].hand)
				print('Table hand: ', table.hand)
				if plkey in playing_hands:
					print('Best type: ', playing_hands_name[plkey])
					print('Best hand: ', playing_hands[plkey])
			

	print(playing_hands)
	return None



"""
flop/turn/river
take the shuffled deck and deal flop/turn/river (updates poker table)
In: random card order, poker table
Out: deck after flop/turn/river, poker table after flop
"""
def flop(deck, table):
	flop_cards, deck = deal(deck, 3, burn=True)
	table.deal(flop_cards)
	return deck

def turn(deck, table):
	turn_cards, deck = deal(deck, 1, burn=True)
	table.deal(turn_cards)
	return deck

def river(deck, table):
	river_cards, deck = deal(deck, 1, burn=True)
	table.deal(river_cards)
	return deck


"""
play_hand
In: small blind, big blind, player dictionary, dealer index, exit signal
"""
def play_hand(sblind, bblind, players, outplayers, dealer, table, exit, game='texasNL'):
	table.new_hand()
	DECK = init_deck()
	NPLAYERS = len(players)
	HANDS, DECK = init_deal(DECK, NPLAYERS)
	assign_hand(dealer, players, HANDS)
	RoundOrder = std_round(players,  table, [sblind, bblind], blind_round=True, game=game)
	DECK = flop(DECK, table)
	print('Flop: ', table.hand)
	RoundOrder += std_round(players,  table, [0, 0], blind_round=False, game=game)
	DECK = turn(DECK, table)
	print('Turn: ', table.hand)
	RoundOrder += std_round(players,  table, [0, 0], blind_round=False, game=game)
	DECK = river(DECK, table)
	print('River: ', table.hand)
	RoundOrder += std_round(players,  table, [0, 0], blind_round=False, game=game)
	showdown(players, table, RoundOrder)

	print('End of round situation:')
	del_players= []
	for plkey in players:
		print(plkey, players[plkey].bank)
		if players[plkey].bank ==0:
			outplayers[plkey] = players[plkey]
			del_players.append(plkey)

	for delkey in del_players:
		players.pop(delkey, None)
	
	#Added while testing before finished (playing one hand)
	#exit.append(True)
	return None
"""
main
"""
def main():
	print("****************************************")
	print("****************POKERPY*****************")
	print("****************************************")
	print("Loading defaults...")
	NHUMAN, NAI, VALUES, KINDS, SMALL_BLIND, BIG_BLIND, CHIPS0,GAME = read_defaults()
	PLAYERS = get_players(NHUMAN, NAI, CHIPS0)
	OUTPLAYERS={}
	NPLAYERS = NHUMAN + NAI
	TABLE = table.poker_table(NPLAYERS)
	DEALER = init_dealer(NPLAYERS)
	EXIT=[]
	while len(PLAYERS)>1 and not True in EXIT:
		print('\n\nHand %d\n' %(len(EXIT)+1))
		play_hand(SMALL_BLIND, BIG_BLIND, PLAYERS, OUTPLAYERS, DEALER, TABLE, EXIT, game=GAME)
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
