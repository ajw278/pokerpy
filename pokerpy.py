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
			elif 'TYPE' in line:
				TYPE = str(line.split('=')[1]).strip()
		except ValueError:
			print('Error reading defaults.')
			sys.exit()

	try:
		return NHUMAN, NAI, VALUES, KINDS, SMALL_BLIND, BIG_BLIND, CHIPS0, GAME, TYPE
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
	IDs = []
	for plyr_key in players:
		IDs.append(players[plyr_key].ID)
	
	IDs = sorted(IDs)

	iID=0
	for ID in IDs:
		for plyr_key in players:
			if players[plyr_key].ID==ID:
				oorder = iID
				players[plyr_key].new_round((oorder+dealer)%nplayers)
				for hand_no in hands_all:
					if players[plyr_key].order==hand_no%nplayers:
						players[plyr_key].deal_cards(hands[hand_no])
	
		
		iID+=1

	
	#Check that deal is correct
	all_hands = []
	print('PLAYERS', players)
	for plkey in players:
		print(players[plkey].order)
		if players[plkey].hand in all_hands:
			print('Repeated hand error.')
			print(hands)
			for plkey2 in players:
				print(plkey2, players[plkey2].order, players[plkey2].hand)
			sys.exit()
		all_hands.append(players[plkey].hand)


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
	if minimum<maximum:
		while bet<minimum or bet>maximum or bet%mindiff!=0:
			print('Bet for %s'%plyrkey)
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
	else:
		while bet!=maximum and bet!='f' and bet!='F':
			print('Bet for %s'%plyrkey)
			print('("f" - fold, "F - fold and show hand,  "h" - see hand, "t" - show table hand)')
			bet = raw_input('Would you like to go all in for %d (type "%d"): ' %(maximum, maximum))
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
		if bet==maximum:
			bet=minimum
	return bet

"""
get_init_deal
Take initial deal information from command line
In: deck, players
Out: deck after deal
"""
def get_init_deal(deck, players, dealer, ncards_tot=2):	
	yes = ['y', 'Y', 'yes', 'Yes']
	no = ['n', 'N', 'no', 'No']

	nplayers = len(players)
	IDs = []
	for plyr_key in players:
		IDs.append(players[plyr_key].ID)
	
	IDs = sorted(IDs)

	iID=0
	for ID in IDs:
		for plyr_key in players:
			if players[plyr_key].ID==ID:
				oorder = iID
				players[plyr_key].new_round((oorder+dealer)%nplayers)
				iID+=1

	for ID in IDs:
		hand_size = 0
		hand_incomplete=True
		for plkey in players:
			if players[plkey].ID==ID:
				while hand_incomplete:
					hand1 = 'na'
					hand2 = 'na'
					y_n_ans = 'na'
					while not hand1 in range(13) and not hand1=='u' :
						hand1 = raw_input('%s card %d value (0-12, "u" for unknown): '%(plkey, hand_size+1))
						try:
							hand1 = int(hand1)
						except ValueError:
							pass
					while not hand2 in range(4) and not hand2=='u' :
						hand2 = raw_input('%s card %d kind (0-3, "u" for unknown): '%(plkey, hand_size+1))
						try:
							hand2 = int(hand2)
						except ValueError:
							pass
					if (hand1=='u' or hand2=='u') and (hand1!='u' or hand2!='u'):
						while not y_n_ans in yes and not y_n_ans in no:
							y_n_ans = ('You have half the hand defined, half unknown. Are you sure?')

						if y_n_ans in yes:
							hand_incomplete=False
							print('This feature not implemented yet.')
							sys.exit()
					elif hand1=='u' and hand2=='u' and players[plkey].ai!=None:
						while not y_n_ans in yes and not y_n_ans in no:
							y_n_ans = ('Undefined hand for AI. Are you sure?')
				
				
						if y_n_ans in yes:
							hand_incomplete=False
							print('This feature not implemented yet.')
							sys.exit()
					elif hand1=='u' and hand2=='u':
						hand_size+=1
					else:
						del_cards = []
						icard = 0
						for card in deck:
							if card.value==hand1 and card.kind==hand2:
								players[plkey].deal_cards([card])
								del_cards.append(icard)
							icard+=1

						if len(del_cards)<1:
							print('No card with value %d and kind %d found in the deck.'%(hand1, hand2))
						elif len(del_cards)>1:
							print('Deck error: found multiple value %d and kind %d in deck.'%(hand1, hand2))
						else:
							print('Dealt to %s: '%plkey, deck[del_cards[0]])
							hand_size+=1
							del deck[del_cards[0]]
						

					if hand_size==ncards_tot:
						hand_incomplete=False
				
	
	return deck

def get_final_hands(deck, players, dealer,  ncards_tot=2):
	for plkey in players:
		if len(players[plkey].hand)<ncards_tot:
			deck = get_init_deal(deck, {plkey: players[plkey]}, \
			dealer, ncards_tot=ncards_tot-len(players[plkey].hand))

	return deck


"""
get_bet
Take betting decision from command line
In: min bet, max bet, multiple of bet, players, key, table
"""
def get_table(deck, table, ncards_tot):	
	yes = ['y', 'Y', 'yes', 'Yes']
	no = ['n', 'N', 'no', 'No']
	ncards=0
	table_incomplete=True
	print('Deal %d cards to table: '%ncards_tot)
	while table_incomplete:
		table1 = 'na'
		table2 = 'na'
		y_n_ans = 'na'
		while not table1 in range(13):
			table1 = raw_input('Table card %d value (0-12, "u" for unknown): '%(ncards+1))
			try:
				table1 = int(table1)
			except ValueError:
				pass
		while not table2 in range(4):
			table2 = raw_input('Table card %d kind (0-3, "u" for unknown): '%(ncards+1))
			try:
				table2 = int(table2)
			except ValueError:
				pass
		
		del_cards = []
		icard = 0
		for card in deck:
			if card.value==table1 and card.kind==table2:
				table.deal([card])
				del_cards.append(icard)
			icard+=1

		if len(del_cards)<1:
			print('No card with value %d and kind %d found in the deck.'%(table1, table2))
		elif len(del_cards)>1:
			print('Deck error: found multiple value %d and kind %d in deck.'%(table1, table2))
			sys.exit()
		else:
			print('Dealt: ', deck[del_cards[0]])
			ncards+=1
			del deck[del_cards[0]]
					

		if ncards==ncards_tot:
			table_incomplete=False
				
	
	return deck

"""
get_dealer
In: nplayers
Out: dealer
"""
def get_dealer(nplayers):
	dealer=nplayers+1
	while dealer<0 or dealer>nplayers-1:
		dealer = raw_input('Initial dealer index (of %d players): ' %(nplayers))
		
		try:
			dealer = int(dealer)
		except ValueError:
			pass

		if type(dealer)!=int:
			bet=minimum-10

	return dealer

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
			bet = player.bank
			bet_check = player.spend(bet)
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

	return bet

"""
round
NOTE: Not sure how to end betting, how many rounds should be allowed
"""
def std_round(players, table, blinds, blind_round=False, game='texasNL'):
	sblind = min(blinds)
	bblind = max(blinds)
	nplayers = len(players)
	inplayers = nplayers
	betplayers=0
	table.new_round()
	bet=0
	new_bet=0
	current=0
	#Bodge job for ending rounds atm 
	RoundFlag=True
	RoundRecord = []
	iround =0

	for plkey in players:
		if players[plkey].betting:
			betplayers+=1

	if 'texasNL' in game:
		if betplayers>1:
			while RoundFlag and inplayers>1: 
				print('Bet number: ', iround, betplayers)
				inplayers = 0
				betplayers=0
				bet_round=False
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
						bet_round=True
						print('%s bets : '%plkey, new_bet, ' for a total of ', table.roundvals[plind], 'this round.')
					#the last player to take aggressive action by a bet or raise is the first to show the hand
					#hence we need a record of who has raised last in each round
					if not players[plkey].fold:
						round_val = np.amax(table.roundvals)
						inplayers+=1
					if players[plkey].betting:
						betplayers+=1
				
				iround +=1
				if iround>nplayers and bet_round:
					RoundFlag=False
					for plkey in players:
						if players[plkey].betting and table.roundvals[players[plkey].order]!=round_val:
							RoundFlag=True
						#print('Round', RoundFlag, plkey, players[plkey].betting)
						#print(table.roundvals[players[plkey].order], players[plkey].order, round_val) 
						
			
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
def showdown(players, table, betorder, deck,dealer, total_orig, gtype='std'):
	if gtype=='manual':
		get_final_hands(deck, players, dealer)
	
	print(betorder)
	playing_hands_name={}
	playing_hands = {}
	playing_values = {}
	max_hand_val =0
	for plkey in players:
		if not players[plkey].fold:
			tot_hand = players[plkey].hand + table.hand
			playing_hands[plkey], playing_values[plkey] = hand.full_hand_best(tot_hand, 5)
			playing_hands_name[plkey] = hand.poker_hand(playing_hands[plkey])
			
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
	
	new_tot=0
	for plkey in players:
		new_tot+=players[plkey].bank

	if new_tot!=total_orig:
		print('Chip number not conserved.')
		sys.exit() 


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
def play_hand(sblind, bblind, players, outplayers, dealer, table, exit, game='texasNL', gtype='std'):
	table.new_hand()
	DECK = init_deck()
	NPLAYERS = len(players)

	ROUNDTOT=0
	for plkey in players:
		ROUNDTOT+=players[plkey].bank
	
	if gtype=='std':
		HANDS, DECK = init_deal(DECK, NPLAYERS)
		assign_hand(dealer, players, HANDS)
	elif gtype=='manual':
		DECK = get_init_deal(DECK, players, dealer)
	else:
		print('Game type not recognised.')
		
	RoundOrder = std_round(players,  table, [sblind, bblind], blind_round=True, game=game)
	if gtype=='std':
		DECK = flop(DECK, table)
	elif gtype=='manual':
		DECK = get_table(DECK, table, 3)
	print('Flop: ', table.hand)
	RoundOrder += std_round(players,  table, [0, 0], blind_round=False, game=game)
	if gtype=='std':
		DECK = turn(DECK, table)
	elif gtype=='manual':
		DECK = get_table(DECK, table, 1)
	print('Turn: ', table.hand)
	RoundOrder += std_round(players,  table, [0, 0], blind_round=False, game=game)
	if gtype=='std':
		DECK = river(DECK, table)
	elif gtype=='manual':
		DECK = get_table(DECK, table, 1)
	print('River: ', table.hand)
	RoundOrder += std_round(players,  table, [0, 0], blind_round=False, game=game)
	showdown(players, table, RoundOrder, DECK,dealer,ROUNDTOT, gtype=gtype)

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
	exit.append(False)
	return None
"""
main
"""
def main():
	print("****************************************")
	print("****************POKERPY*****************")
	print("****************************************")
	print("Loading defaults...")
	NHUMAN, NAI, VALUES, KINDS, SMALL_BLIND, BIG_BLIND, CHIPS0,GAME, TYPE = read_defaults()
	PLAYERS = get_players(NHUMAN, NAI, CHIPS0)
	OUTPLAYERS={}
	NPLAYERS = NHUMAN + NAI
	TABLE = table.poker_table(NPLAYERS)
	if TYPE=='std':
		DEALER = init_dealer(NPLAYERS)
	elif TYPE=='manual':
		DEALER = get_dealer(NPLAYERS)
	else:
		print('Game type not recognised.')
		print(TYPE, 'manual', TYPE=='manual')
		for it in range(len(TYPE)):
			print(TYPE[it], 'manual'[it])
		sys.exit()
	EXIT=[]
	while len(PLAYERS)>1 and not True in EXIT:
		print('\n\nHand %d\n' %(len(EXIT)+1))
		print('Dealer: ', DEALER)
		play_hand(SMALL_BLIND, BIG_BLIND, PLAYERS, OUTPLAYERS, DEALER, TABLE, EXIT, game=GAME, gtype=TYPE)
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
