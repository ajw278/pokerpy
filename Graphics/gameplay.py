#!/usr/bin/python

"""
Notes:
"""
from __future__ import print_function


import pygame
 
import sys
import pokerpy
import im_objects
import player
import table
import random
import entry
import hand
import numpy as np
import time
import copy

from socket import *
#from menu import *
from pygame.locals import *

pygame.init()
 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

value_chars = '0123456789jqka'
kind_chars = 'cdshCDSH'
number_chars='0123456789'
letter_chars ='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'



class GameGraphics():
	def __init__(self, gstate, ai_players, hum_players, fontObj):
		self.screen = gstate.screen
		self.scr_rect = self.screen.get_rect()
		player_boxes, AI_boxes, dealer_box, deal_button = im_objects.position_boxes(self.scr_rect.width, self.scr_rect.height, 2, 5, ai_players, hum_players, fontObj, gstate.dealer)
		
		box_dict = {}
		iplyr=0
		for hplyr in hum_players:
			box_dict[hplyr.ID] = player_boxes[iplyr]
			iplyr+=1

		iplyr=0
		for hplyr in ai_players:
			box_dict[hplyr.ID] = AI_boxes[iplyr]
			iplyr+=1
		
		self.tbox = dealer_box
		self.pboxes = box_dict
		self.button = deal_button



	def update_all(self, gstate):
		for key in gstate.players:
			self.pboxes[key].update(gstate.players[key])
			s = pygame.Surface((self.pboxes[key].coords[2],self.pboxes[key].coords[3]))  # the size of your rect
			s.set_alpha(100)       # alpha level
			if not gstate.players[key].turn:
				gstate.graphics.pboxes[key].turn_off()
				s.fill((0,0,0)) 
			else:
				gstate.graphics.pboxes[key].turn_on()
				s.fill((255,0,0))
			self.screen.blit(s, (self.pboxes[key].coords[0],self.pboxes[key].coords[1]))    # (0,0) are the top-left coordinates
			for card in self.pboxes[key].cards:
				self.screen.blit(card.image, card.rect)
			for itxt in range(len(self.pboxes[key].text)):
				self.screen.blit(self.pboxes[key].text[itxt], self.pboxes[key].textloc[itxt])

		

		self.tbox.update(gstate.table)
		s = pygame.Surface((self.tbox.coords[2],self.tbox.coords[3]))  # the size of your rect
		s.set_alpha(100)                # alpha level
		s.fill((0,0,0))           # this fills the entire surface
		self.screen.blit(s, (self.tbox.coords[0],self.tbox.coords[1]))    # (0,0) are the top-left coordinates

		for card in self.tbox.cards:
			self.screen.blit(card.image, card.rect)
		for itxt in range(len(self.tbox.text)):
			self.screen.blit(self.tbox.text[itxt], self.tbox.textloc[itxt])

		self.button.move_button(gstate.dealer)
		self.screen.blit(self.button.image, self.button.rect)

		print('Dealer: ', gstate.dealer)
		print('Order:')
		for plkey in gstate.players:
			print(plkey, ': ', gstate.players[plkey].order)

		return None


"""
class, GameState

To do: Initialise as either the randomised version, or player defined
"""
class GameState():
	def __init__(self, nplayers,chips0,blinds, mindiff, fontObj=None, dealer=None, screen=None):
		hum_players = []
		ai_players = []
		self.playing=0
		if dealer==None:
			self.dealer = random.randint(0, nplayers-1)
		else:
			self.dealer = dealer
		
		for iplayer in range(nplayers):
			if iplayer == 0:
				hum_players.append(player.player(chips0, iplayer, None))
			else:
				ai_players.append(player.player(chips0, iplayer, 'basic'))
		state=1
		#Need to associate players with their boxes - not all that important but done a little haphazardly..
		player_dict = {}
		iplyr=0
		for hplyr in hum_players:
			player_dict[hplyr.ID] = hplyr
			iplyr+=1

		iplyr=0
		for hplyr in ai_players:
			player_dict[hplyr.ID] = hplyr
			iplyr+=1
		self.aips = ai_players
		self.hps = hum_players
		self.players = player_dict
		self.screen =screen
		self.aips = ai_players
		self.hps = hum_players
		self.fontObj = fontObj
		if self.screen!=None:
			self.graphics = GameGraphics(self, ai_players, hum_players, fontObj)
		else:
			self.graphics = None

		self.blinds = blinds
		self.schip = mindiff
		self.state=1
		self.deck = pokerpy.init_deck()
		self.betplayers = 0
		self.nplayers = len(self.players)
		self.iround = 0
		self.roundorder = []
		for plkey in self.players:
			if self.players[plkey].betting:
				self.betplayers+=1
		self.inplayers =0
		for plkey in self.players:
			if not self.players[plkey].fold and not self.players[plkey].out:
				self.inplayers+=1
		for plkey in self.players:
			if not self.players[plkey].out:
				self.playing+=1

		self.table = table.poker_table(self)

	def move_dealer(self):
		NoDealer = True
		nloops=0
		while NoDealer:
			self.dealer+=1
			self.dealer = self.dealer%self.nplayers
			for plkey in self.players:
				if self.players[plkey].ID==self.dealer and not self.players[plkey].out:
					NoDealer=False

			nloops+=1
			if nloops>self.nplayers+1:
				print('Dealer search error.')
				sys.exit()

	def new_hand(self):
		for plkey in self.players:
			if self.players[plkey].bank>0:
				self.players[plkey].new_round()
			else:
				self.players[plkey].eliminate()
		self.update_players()
		self.roundorder=[]
		self.deck = pokerpy.init_deck()
		self.table.new_hand(self)
		cardset, self.deck = pokerpy.init_deal(self.deck, self.playing)
		pokerpy.assign_hand(self.dealer, self.players, cardset)
		self.state=2
		self.iround=0

	
	def make_bet(self,plkey, bet):
		if type(bet)!=str:
			bet_check = self.players[plkey].spend(bet)
			err_flag = False
			i_flag=0
			while not bet_check and not err_flag:
				print('Bet too high for player. Betting all in...')
				bet = self.players[plkey].bank
				bet_check = self.players[plkey].spend(bet)
				i_flag+=1
				if i_flag>2:
					err_flag=True
			
			if err_flag:
				print('Error in betting.')
				sys.exit()
		
			self.table.bid(bet, self.players[plkey].order)
		else:
			if bet=='f':
				self.players[plkey].hand_fold(False)
			elif bet=='F':
				self.players[plkey].hand_fold(True)
			else:
				print('Bet signal "%s" not recognised.'%bet)
				sys.exit()

		self.update_players()

		return bet

	def new_round(self):
		self.iround = 0
		self.table.new_round(self)

	def next_round(self):
		self.iround+=1

	def reset_round(self):
		self.iround=0

	def update_players(self):
		self.betplayers =0
		self.inplayers=0
		self.playing=0
		for plkey in self.players:
			#print(plkey)
			if self.players[plkey].betting:
				#print(plkey, 'betting')
				self.betplayers+=1
			if not self.players[plkey].fold and not self.players[plkey].out:
				#print(plkey, 'unfolded')
				self.inplayers+=1
			if not self.players[plkey].out:
				self.playing+=1
		
	def eliminate_players(self):
		for plkey in self.players:
			if self.players[plkey].bank==0:
				self.players[plkey].eliminate()
			else:
				print(plkey, ' not eliminated.')

		self.update_players()


	def add_record(self,record):
		self.roundorder+=record

	def new_state(self, nstate):
		self.state=nstate

	def payout(self, win_inds, tbreak):
		payouts = self.table.payout(win_inds, tbreak, self.schip)
		for plkey in self.players:
			if not self.players[plkey].out:
				self.players[plkey].win(payouts[self.players[plkey].order])
		return payouts
	"""
	flop/turn/river
	take the shuffled deck and deal flop/turn/river (updates poker table)
	In: random card order, poker table
	Out: deck after flop/turn/river, poker table after flop
	"""
	def flop(self, set_cards=None):
		if set_cards==None:
			flop_cards, self.deck = pokerpy.deal(self.deck, 3, burn=True)
		else:
			flop_cards = set_cards
			self.deck.remove(flop_cards[0])
			self.deck.remove(flop_cards[1])
			self.deck.remove(flop_cards[2])
		self.table.deal(flop_cards)

	def turn(self, set_cards=None):
		if set_cards==None:
			turn_cards, self.deck = pokerpy.deal(self.deck, 1, burn=True)
		else:
			turn_cards=set_cards
			self.deck.remove(turn_cards[0])
		self.table.deal(turn_cards)

	def river(self, set_cards=None):
		if set_cards==None:
			river_cards, self.deck = pokerpy.deal(self.deck, 1, burn=True)
		else:
			river_cards = set_cards
			self.deck.remove(river_cards[0])
		self.table.deal(river_cards)

	def show_hands(self):
		for plkey in self.players:
			if self.players[plkey].betting:
				self.players[plkey].show_hand()

	def copy_game(self, gstate, screen=None):
		
		self.playing=gstate.playing
		self.dealer = gstate.dealer
		self.players = gstate.players
		self.screen =screen
		self.aips = gstate.aips
		self.hps = gstate.hps
		self.hps = gstate.hps	
		self.blinds = gstate.blinds
		self.schip = gstate.schip
		self.state= gstate.state
		self.deck = gstate.deck
		self.betplayers = gstate.betplayers
		self.nplayers = len(self.players)
		self.iround = gstate.iround
		self.roundorder = gstate.roundorder
		for plkey in self.players:
			if self.players[plkey].betting:
				self.betplayers+=1
		self.inplayers =0
		for plkey in self.players:
			if not self.players[plkey].fold and not self.players[plkey].out:
				self.inplayers+=1
		for plkey in self.players:
			if not self.players[plkey].out:
				self.playing+=1

		self.table = gstate.table
		self.update_players()
		
		if self.screen!=None:
			self.graphics = GameGraphics(self, self.aips, self.hps, self.fontObj)
		else:
			self.graphics = None

		if self.graphics!=None:
			self.graphics.update_all(self)


def dummy_func(*args):
	print('Not implemented yet.')
	sys.exit()

class DummyOptions():
	def __init__(self):
		self.items = []

def ask(screen, gstate, font,font_color=(255,0,0), restrict='all', maxlen=20, prompt_string='Enter: ', pgame=None):

	scw = screen.get_rect().width
	sch = screen.get_rect().height
	options = DummyOptions()
	
	txtbx = entry.Input(maxlength=maxlen, color=font_color, x=int(float(scw)/2.), y=int(0.35*float(sch)), font=font, prompt=prompt_string)
	while True:
		# events for txtbx
		events = pygame.event.get()
		if not pgame==None:
			print('Tick in ask..')
			ret_val = pgame.tick([v for v in gstate.graphics.pboxes.values()], events=events, gstate = gstate)
			if ret_val!=None:
				return ['exit', ret_val]
		# process other events
		for event in events:
			if event.type == pygame.KEYDOWN:
				inkey = event.key
				if (inkey == K_RETURN or inkey == K_KP_ENTER):
					return txtbx.value
		s = pygame.Surface((scw,font.get_height()+5))
		srect = s.get_rect()
		srect.center =(txtbx.x,txtbx.y)
		#s.set_alpha(100)                # alpha level
		s.fill((0,0,0))           # this fills the entire surface
		screen.blit(s, srect)
		# update txtbx
		txtbx.update(events)
		# blit txtbx on the sceen
		txtbx.draw(screen)
		
		pygame.display.flip()


def ask_bet(pgame,gstate,plyrkey):

	minimum = np.amax(gstate.table.roundvals) - gstate.table.roundvals[gstate.players[plyrkey].order]
	maximum = gstate.players[plyrkey].bank

	bet = minimum-10
	if minimum<maximum:
		while bet<minimum or bet>maximum or bet%gstate.schip!=0:
			print('Bet for %s'%plyrkey)
			pgame.screen.fill(pgame.bg_color)
			gstate.graphics.update_all(gstate)
			bet = ask(pgame.screen, gstate, pgame.fontObj, prompt_string = 'Bet (in multiples %s) between %d and %d: ' %(gstate.schip, minimum, maximum), pgame=pgame)
			if bet=='f' or bet=='F':
				break
			elif type(bet)==list:
				bet[0]='exit'
				return bet[1]

			try:
				bet = int(bet)
			except ValueError:
				pass

			if type(bet)!=int:
				bet=minimum-10
	else:
		while bet!=maximum and bet!='f' and bet!='F':
			bet = ask(pgame.screen, gstate, pgame.fontObj, prompt_string = 'Would you like to go all in for %d (type "%d"): '%(maximum, maximum), pgame=pgame)
			if bet=='f' or bet=='F':
				break

			try:
				bet = int(bet)
			except ValueError:
				pass
		if bet==maximum:
			bet=minimum
	return bet


def std_round(pgame, gstate,  blind_round=False, display=None, fontObj=None):
	RoundFlag=True
	bet=0
	new_bet=0
	current=0
	bet_offset=0
	round_val = np.amax(gstate.table.roundvals)
	RoundRecord=[]
	gstate.update_players()
	if gstate.betplayers>1:
		while RoundFlag and gstate.inplayers>1: 
			print('Bet number: ', gstate.iround)
			print('Players in: ', gstate.inplayers)
			bet_round=False
			for plkey in gstate.players:

				print(plkey, ': ', gstate.players[plkey].order, gstate.iround,gstate.playing, gstate.players[plkey].out)
				print('betting - ', gstate.players[plkey].betting)

				if gstate.players[plkey].order==gstate.iround%gstate.playing and not gstate.players[plkey].out and  gstate.players[plkey].betting:
					gstate.players[plkey].start_turn()
					pgame.blit_gstate(gstate)
					plind = gstate.players[plkey].order
					if blind_round:
						print('DEBUG 1')
						if gstate.iround==0+bet_offset:
							print('%s bets small blind: %d' %(plkey, gstate.blinds[0]))
							new_bet=gstate.blinds[0]
						elif gstate.iround==1+bet_offset:
							print('%s bets big blind: %d' %(plkey, gstate.blinds[1]))
							new_bet=gstate.blinds[1]
					if (not blind_round) or (not (gstate.iround==1 or gstate.iround==0)):
						print('DEBUG 2')
						if gstate.players[plkey].ai == None:
							print('DEBUG 3')
							if display!=None:
								new_bet = ask_bet(pgame, gstate,plkey)
								if type(new_bet)==str and new_bet not in ['f','F']:
									return new_bet
							else:
								new_bet = dummy_func(gstate.players,plkey,gstate.table)
						else:
							new_bet = gstate.players[plkey].choose_bet(gstate.players, gstate.table)
					if new_bet>np.amax(gstate.table.roundvals):
						RoundRecord.append(gstate.players[plkey].ID)
					gstate.make_bet(plkey, new_bet)
					bet_round=True
					print('%s bets : '%plkey, new_bet, ' for a total of ', gstate.table.roundvals[plind], 'this round.')
					gstate.players[plkey].end_turn()
					pgame.blit_gstate(gstate)
					break
				elif gstate.players[plkey].order==gstate.iround%gstate.playing and not gstate.players[plkey].betting:
					bet_offset+=1
					bet_round=True
					break

					
				#the last player to take aggressive action by a bet or raise is the first to show the hand
				#hence we need a record of who has raised last in each round
				if not gstate.players[plkey].fold:
					round_val = np.amax(gstate.table.roundvals)
				
			
			gstate.update_players()
			if bet_round:
				gstate.next_round()
			if gstate.iround>=gstate.nplayers or gstate.betplayers==0:
				RoundFlag=False
				for plkey in gstate.players:
					if gstate.players[plkey].betting and gstate.table.roundvals[gstate.players[plkey].order]!=round_val:
						RoundFlag=True
					#print('Round', RoundFlag, plkey, players[plkey].betting)
					#print(table.roundvals[players[plkey].order], players[plkey].order, round_val) 
		
		gstate.reset_round()			
		
		bet=new_bet
		new_bet='error'
		#Define here current min bet size
		print('Players remaining unfolded: ', gstate.inplayers)
		print('Players in game: ', gstate.betplayers)

		gstate.add_record(RoundRecord)
		
		return None



"""
showdown
Convoluted and unecessarily complicated right now... need to check all this
In: Players, table, betting order (not used atm, for the reveal if needed)

"""
def showdown(pgame, gstate, gtype=None):
	if gtype=='manual':
		get_final_hands(deck, players, dealer)

	gstate.show_hands()
	pgame.blit_gstate(gstate)
	
	playing_hands_name={}
	playing_hands = {}
	playing_values = {}
	tiebreak_values = {}
	max_hand_val =0
	for plkey in gstate.players:
		if not gstate.players[plkey].fold and not gstate.players[plkey].out:
			tot_hand = gstate.players[plkey].hand + gstate.table.hand
			playing_hands[plkey], playing_values[plkey] = hand.full_hand_best(tot_hand, 5)
			tiebreak_values[plkey] = hand.tiebreaker(gstate.players[plkey].hand)
			playing_hands_name[plkey] = hand.poker_hand(playing_hands[plkey])
			
	for plkey in playing_hands:
		max_hand_val = max(max_hand_val, playing_values[plkey])

	win_inds = []
	tbreak_vals = []

	for plkey in playing_hands:
		if playing_values[plkey]==max_hand_val:
			win_inds.append(gstate.players[plkey].order)
			tbreak_vals.append(tiebreak_values[plkey])
	
	payouts = gstate.payout(win_inds, tbreak_vals)
	
	for ipay in range(len(payouts)):
		for plkey in gstate.players:
			if gstate.players[plkey].order==ipay:
				print('\nWinnings for %s: %d'%(plkey, payouts[ipay]))
				print('Hand: ', gstate.players[plkey].hand)
				print('Table hand: ', gstate.table.hand)
				if plkey in playing_hands:
					print('Best type: ', playing_hands_name[plkey])
					print('Best hand: ', playing_hands[plkey])
	
	time.sleep(5)
	
	px = pgame.screen.get_rect().width/2

	sch = pgame.screen.get_rect().height
	py_mid = sch/2
	py = np.linspace(-0.3,0.3, gstate.playing)

	pgame.screen.fill((0,0,0))

	ipy=0
	for plkey in gstate.players:
		if not gstate.players[plkey].out:
			if plkey in playing_hands_name:
				hand_name = playing_hands_name[plkey]
			else:
				hand_name = 'fold'
			win_text= pgame.fontObj.render("Player {0.ID} ({1}): {2}".format(gstate.players[plkey], hand_name,payouts[gstate.players[plkey].order] ), 1, (255,0,0))
			win_rect = win_text.get_rect()
			win_rect.center = (px, py_mid+py[ipy]*sch)
			pgame.screen.blit(win_text, win_rect)
			ipy+=1
			
	pygame.display.flip()
	time.sleep(5)
	
	new_tot=0
	for plkey in gstate.players:
		new_tot+=gstate.players[plkey].bank

	print('________________\nShowdown Summary:')
	print('Playing hands:')
	for plkey in playing_hands:
		print(plkey, ': ', playing_hands[plkey])
	
	print('\nTotal in bank: ', new_tot)
	print('\nPayouts: ', payouts)
	print('________________')
	return None


def winner_screen(pgame, gstate):

	pgame.screen.fill((0,0,0))
	px = pgame.screen.get_rect().width/2
	py = pgame.screen.get_rect().height/2
	for plkey in gstate.players:
		if gstate.players[plkey].betting:
			win_text= pgame.fontObj.render("Winner: Player {0.ID} ({0.bank})".format(gstate.players[plkey]), 1, (255,0,0))
			win_rect = win_text.get_rect()
			win_rect.center = (px, py)
			pgame.screen.blit(win_text, win_rect)
			
	pygame.display.flip()
	pygame.display.flip
	time.sleep(10)
	return None


"""
Items must now conform to the definition here
"""

class PokerGame():
	def __init__(self, screen, items, gamefontObj,bg_color=BLACK, game_type='auto'):
		self.screen = screen
		self.gtype = game_type
		self.scr_width = self.screen.get_rect().width
		self.scr_height = self.screen.get_rect().height
		self.fontObj = gamefontObj
		#self.font = font
		self.bg_color = bg_color
		self.clock = pygame.time.Clock()

		self.items = []
		for index, item in enumerate(items):
			self.items.append(item)

		self.mouse_is_visible = True
		self.cur_item = None
 
	"""def set_mouse_visibility(self, optObj=None):
		if optObj==None:
			optObj=self
		if optObj.mouse_is_visible:
			pygame.mouse.set_visible(True)
		else:
			pygame.mouse.set_visible(False)"""

	def set_keyboard_selection(self, key, optObj=None):
		if optObj==None:
			optObj = self
		if len(optObj.items)>0:
			for item in optObj.items:
				# Return all to neutral
				item.set_italic(False)
				item.set_font_color(WHITE)

			if obtObj.cur_item is None:
				optObj.cur_item = 0
			else:
				# Find the chosen item
				if key == pygame.K_UP and \
				optObj.cur_item > 0:
					optObj.cur_item -= 1
				elif key == pygame.K_UP and \
				optObj.cur_item == 0:
					optObj.cur_item = len(optObj.items) - 1
				elif key == pygame.K_DOWN and \
				optObj.cur_item < len(optObj.items) - 1:
					optObj.cur_item += 1
				elif key == pygame.K_DOWN and \
				optObj.cur_item == len(optObj.items) - 1:
					optObj.cur_item = 0

			optObj.items[optObj.cur_item].set_italic(True)
			optObj.items[optObj.cur_item].set_font_color(RED)

			# Finally check if Enter or Space is pressed
			if key == pygame.K_SPACE or key == pygame.K_RETURN:
				text = optObj.items[optObj.cur_item].text
				return text
 	"""
	def set_mouse_selection(self, item, mpos):
		if item.is_mouse_selection(mpos):
			item.set_font_color(RED)
			item.set_italic(True)
		else:
			item.set_font_color(WHITE)
			item.set_italic(False)"""


	def set_mouse_visibility(self):
		if self.mouse_is_visible:
			pygame.mouse.set_visible(True)
		else:
			pygame.mouse.set_visible(False)
	
 
    	def set_keyboard_selection(self, key):
		"""
		Marks the MenuItem chosen via up and down keys.
		"""
		for item in self.items:
			# Return all to neutral
			item.set_neutral()
	 
		if self.cur_item is None:
			self.cur_item = 0
		else:
			# Find the chosen item
			if key == pygame.K_UP and \
				self.cur_item > 0:
				self.cur_item -= 1
			elif key == pygame.K_UP and \
				self.cur_item == 0:
				self.cur_item = len(self.items) - 1
			elif key == pygame.K_DOWN and \
				self.cur_item < len(self.items) - 1:
				self.cur_item += 1
			elif key == pygame.K_DOWN and \
				self.cur_item == len(self.items) - 1:
				self.cur_item = 0

		self.items[self.cur_item].set_italic(True)
		self.items[self.cur_item].set_font_color(RED)
 
		# Finally check if Enter or Space is pressed
		if key == pygame.K_SPACE or key == pygame.K_RETURN:
			text = self.items[self.cur_item].text
			return text

		return None

	def run(self, state, nplayers,chips0, blinds, mindiff, gstate=None):
		mainloop = True
		prev_state=-1

		if gstate!=None:
			gstate_new = GameState(gstate.nplayers,chips0, gstate.blinds, gstate.schip, fontObj=self.fontObj, screen=self.screen)
			gstate_new.copy_game(gstate, screen=self.screen)
			gstate = copy.copy(gstate_new)

		while mainloop:

			#State=0 --> init game
			#State=1 --> deal
			#State=2 --> play, blind
			update_flag=False
			ret_val=None

			if gstate!=None:
				ROUND_TOT=0
				for plkey in gstate.players:
					ROUND_TOT+=gstate.players[plkey].bank
				ROUND_TOT+=gstate.table.pot

				ROUND_TOT=copy.copy(ROUND_TOT)
			if state==0 or gstate==None:
				rect_list = []
				#Assign players to list
				gstate = GameState(nplayers,chips0, blinds, mindiff, fontObj=self.fontObj, screen=self.screen)
				state=1
			elif gstate.state==1:

				gstate.move_dealer()
				#self.screen.blit(mbg, (CENTER[0]-SCW/2,CENTER[1]-SCH/2))
				gstate.new_hand()
				
				ROUND_TOT=0
				for plkey in gstate.players:
					print('Bank {0}: {1}'.format(plkey, gstate.players[plkey].bank))
					ROUND_TOT+=gstate.players[plkey].bank
				ROUND_TOT+=gstate.table.pot

				ROUND_TOT=copy.copy(ROUND_TOT)
			elif gstate.state==2:
				ret_val = std_round(self, gstate, blind_round=True, display = self.screen)
				if ret_val==None:
					gstate.new_round()
					gstate.new_state(3)
					if self.gtype=='auto':
						gstate.flop()
					else:
						cards = gstate.graphics.tbox.response('flop')
						gstate.flop(cards)
			elif gstate.state==3:
				ret_val =std_round(self, gstate, blind_round=False, display = self.screen)
				if ret_val==None:
					gstate.new_round()
					gstate.new_state(4)
					if self.gtype=='auto':
						gstate.turn()
					else:
						cards = gstate.graphics.tbox.response('turn')
						gstate.turn(cards)
			elif gstate.state==4:
				ret_val =std_round(self, gstate, blind_round=False, display = self.screen)
				if ret_val==None:
					gstate.new_round()
					gstate.new_state(5)
					if self.gtype=='auto':
						gstate.river()
					else:
						cards = gstate.graphics.tbox.response('river')
						gstate.river(cards)
			elif gstate.state==5:
				ret_val =std_round(self, gstate, blind_round=False, display = self.screen)
				if ret_val==None:
					showdown(self, gstate)
					gstate.eliminate_players()
					gstate.update_players()
					ROUND_TOT_NEW=0
					for plkey in gstate.players:
						ROUND_TOT_NEW+=gstate.players[plkey].bank
					if ROUND_TOT!=ROUND_TOT_NEW:
						print('Error: chip bank discrepancy.')
						print('Opened with %d, closed with %d'%(ROUND_TOT,ROUND_TOT_NEW))
						sys.exit()
					if gstate.playing>1:
						gstate.new_state(1)
					else:
						gstate.new_state(6)
			elif gstate.state==6:
				winner_screen(self, gstate)
				return gstate, 'menu'
			else:
				print('Game state error.')
				sys.exit()

			if ret_val!=None:
				return gstate, ret_val

			if gstate.state!=prev_state:
				self.tick(None, gstate=gstate)
			else:
				self.tick([ v for v in gstate.graphics.pboxes.values()], gstate=gstate)
			prev_state=gstate.state


	#NEED TO MOVE RESPONSES INTO TICK()

	def tick(self, optObj, events=None, gstate=None):

		if events==None:
			events=pygame.event.get()

		if gstate!=None:
			# Redraw the background
			self.blit_gstate(gstate)
		
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_SPACE]:
			return 'pausemenu'
		self.clock.tick(50)

		mpos = pygame.mouse.get_pos()
		for event in events:
			if event.type == pygame.QUIT:
				mainloop = False
			"""if event.type == pygame.KEYDOWN:
				self.mouse_is_visible = False
				if optObj!=None:
					print(optObj)
					self.set_keyboard_selection(event.key)
					keyslct = self.set_keyboard_selection(event.key)
					if keyslct!=None:
						return keyslct"""
			if event.type == pygame.MOUSEBUTTONDOWN:
				if optObj!=None:
					print(optObj)
					for item in optObj:
						if item.is_mouse_selection(mpos):
							response = item.response(self.screen)
							return response
		
		if pygame.mouse.get_rel() != (0, 0):
			self.mouse_is_visible = True
			self.cur_item = None

		self.set_mouse_visibility()

		if optObj!=None:
			for item in optObj:
				if self.mouse_is_visible:
					item.set_mouse_selection(mpos, self.screen)
				#self.screen.blit(item.label, item.position)
		
		pygame.display.flip()


		
		return None

	

	def blit_gstate(self, gstate):
		self.screen.fill(self.bg_color)
		gstate.graphics.update_all(gstate)
			
		pygame.display.flip()
 
if __name__ == "__main__":
    def hello_world():
        print("Hello World!")
 
    # Creating the screen
    screen = pygame.display.set_mode((640, 480), 0, 32)
 
    menu_items = ('Start', 'Quit')
    funcs = {'Start': hello_world,
             'Quit': sys.exit}
 
    pygame.display.set_caption('Game Menu')
    gm = GameMenu(screen, menu_items)
    gm.run()
 
