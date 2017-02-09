#!/usr/bin/python

"""
Notes:
- Not sure the right nplayers being used - need to check when players are knocked out
- A lot of errors regarding who is out, who is allowed to bet and pot division
"""
from __future__ import print_function


import pygame
 
import sys
import pygame
import pokerpy
import im_objects
import player
import table
import random
import entry
import hand
import numpy as np
import time

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


"""
class, GameState
If I was doing this properly there should be a class which holds
all the game state data and a class which contains that class plus
all the graphical data. Probably won't be too hard to correct later.
For the time being, this holds the game state for the graphical version,
including graphical data
"""
class GameState():
	def __init__(self,scw, sch, nplayers,chips0,blinds, textfontObj):
		hum_players = []
		ai_players = []
		for iplayer in range(nplayers):
			if iplayer == 0:
				hum_players.append(player.player(chips0, iplayer, None))
			else:
				ai_players.append(player.player(chips0, iplayer, 'basic'))
		state=1
		table_data = table.poker_table(nplayers)
		#Define the card dimensions and positions 
		player_boxes, AI_boxes, dealer_box = im_objects.position_boxes(scw, sch, 2, 5, ai_players, hum_players, textfontObj)

		#Need to associate players with their boxes - not all that important but done a little haphazardly..
		player_dict = {}
		box_dict = {}
		iplyr=0
		for hplyr in hum_players:
			player_dict[hplyr.ID] = hplyr
			box_dict[hplyr.ID] = player_boxes[iplyr]
			iplyr+=1

		iplyr=0
		for hplyr in ai_players:
			player_dict[hplyr.ID] = hplyr
			box_dict[hplyr.ID] = AI_boxes[iplyr]
			iplyr+=1
		#Define the initial dealer
		self.blinds = blinds
		self.table = table_data
		self.tbox = dealer_box
		self.players = player_dict
		self.pboxes = box_dict
		self.dealer = random.randint(0, nplayers-1)
		self.state=1
		self.deck = pokerpy.init_deck()
		self.inplayers = 0
		self.nplayers = len(self.players)
		self.iround = 0
		self.roundorder = []
		for plkey in self.players:
			if self.players[plkey].betting:
				self.inplayers+=1
		self.betplayers =0
		for plkey in self.players:
			if not self.players[plkey].fold and self.players[plkey].betting:
				self.inplayers+=1

	def move_dealer(self,iplayer):
		self.dealer = iplayer%self.inplayers

	def new_hand(self):
		self.roundorder=[]
		self.deck = pokerpy.init_deck()
		self.table.new_hand()
		cardset, deck = pokerpy.init_deal(self.deck, self.table.nplayers)
		pokerpy.assign_hand(self.dealer, self.players, cardset)
		self.state=2
		self.iround=0

	
	def update_all(self, display_surface):
		for key in self.players:
			self.pboxes[key].update(self.players[key])
			s = pygame.Surface((self.pboxes[key].coords[2],self.pboxes[key].coords[3]))  # the size of your rect
			s.set_alpha(100)                # alpha level
			s.fill((0,0,0))           # this fills the entire surface
			display_surface.blit(s, (self.pboxes[key].coords[0],self.pboxes[key].coords[1]))    # (0,0) are the top-left coordinates
			for card in self.pboxes[key].cards:
				display_surface.blit(card.image, card.rect)
			for itxt in range(len(self.pboxes[key].text)):
				display_surface.blit(self.pboxes[key].text[itxt], self.pboxes[key].textloc[itxt])

		self.tbox.update(self.table)
		s = pygame.Surface((self.tbox.coords[2],self.tbox.coords[3]))  # the size of your rect
		s.set_alpha(100)                # alpha level
		s.fill((0,0,0))           # this fills the entire surface
		display_surface.blit(s, (self.tbox.coords[0],self.tbox.coords[1]))    # (0,0) are the top-left coordinates

		for card in self.tbox.cards:
			display_surface.blit(card.image, card.rect)
		for itxt in range(len(self.tbox.text)):
			display_surface.blit(self.tbox.text[itxt], self.tbox.textloc[itxt])

		return None

	
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

		return bet

	def next_round(self):
		self.iround+=1

	def reset_round(self):
		self.iround=0

	def update_players(self):
		self.inplayers =0
		self.betplayers=0
		for plkey in self.players:
			print(plkey)
			if self.players[plkey].betting:
				print(plkey, 'betting')
				self.inplayers+=1
			if not self.players[plkey].fold:
				print(plkey, 'unfolded')
				self.betplayers+=1
		
	def eliminate_players(self):
		for plkey in self.players:
			if self.players[plkey].bank==0:
				self.players[plkey].eliminate()

		self.update_players()


	def add_record(self,record):
		self.roundorder+=record

	def new_state(self, nstate):
		self.state=nstate

	def payout(self, win_inds):
		payouts = self.table.payout(win_inds)
		for plkey in self.players:
			self.players[plkey].win(payouts[self.players[plkey].order])
		


	"""
	flop/turn/river
	take the shuffled deck and deal flop/turn/river (updates poker table)
	In: random card order, poker table
	Out: deck after flop/turn/river, poker table after flop
	"""
	def flop(self):
		flop_cards, self.deck = pokerpy.deal(self.deck, 3, burn=True)
		self.table.deal(flop_cards)

	def turn(self):
		turn_cards, self.deck = pokerpy.deal(self.deck, 1, burn=True)
		self.table.deal(turn_cards)

	def river(self):
		river_cards, self.deck = pokerpy.deal(self.deck, 1, burn=True)
		self.table.deal(river_cards)


def dummy_func(*args):
	print('Not implemented yet.')
	sys.exit()

def ask(screen, font,font_color=(255,0,0), restrict='all', maxlen=20, prompt_string='Enter: '):

	scw = screen.get_rect().width
	sch = screen.get_rect().height
	txtbx = entry.Input(maxlength=maxlen, color=font_color, x=int(float(scw)/2.), y=int(0.35*float(sch)), font=font, prompt=prompt_string)
	while True:
		# events for txtbx
		events = pygame.event.get()
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
		
		# refresh the display
		pygame.display.flip()

def ask_bet(pgame,gstate,plyrkey):

	mindiff=5
	minimum = np.amax(gstate.table.roundvals) - gstate.table.roundvals[gstate.players[plyrkey].order]
	maximum = gstate.players[plyrkey].bank

	bet = minimum-10
	if minimum<maximum:
		while bet<minimum or bet>maximum or bet%mindiff!=0:
			print('Bet for %s'%plyrkey)
			pgame.screen.fill(pgame.bg_color)
			gstate.update_all(pgame.screen)
			bet = ask(pgame.screen, pgame.fontObj, prompt_string = 'Bet (in multiples %s) between %d and %d: ' %(mindiff, minimum, maximum))
			if bet=='f' or bet=='F':
				break

			try:
				bet = int(bet)
			except ValueError:
				pass

			if type(bet)!=int:
				bet=minimum-10
	else:
		while bet!=maximum and bet!='f' and bet!='F':
			bet = ask(pgame.screen, pgame.fontObj, prompt_string = 'Would you like to go all in for %d (type "%d"): '%(maximum, maximum))
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
	round_val = np.amax(gstate.table.roundvals)
	RoundRecord=[]
	gstate.update_players()
	if gstate.inplayers>1:
		while RoundFlag and gstate.betplayers>1: 
			print('Bet number: ', gstate.iround)
			print('Players in: ', gstate.betplayers)

			bet_round=False
			for plkey in gstate.players:
				if gstate.players[plkey].order==gstate.iround%gstate.nplayers and gstate.players[plkey].betting:
					plind = gstate.players[plkey].order
					if gstate.players[plkey].ai != None:
						print('AI player.')
					if blind_round:
						if gstate.iround==0:
							print('%s bets small blind: %d' %(plkey, gstate.blinds[0]))
							new_bet=gstate.blinds[0]
						elif gstate.iround==1:
							print('%s bets big blind: %d' %(plkey, gstate.blinds[1]))
							new_bet=gstate.blinds[1]
					if (not blind_round) or (not (gstate.iround==1 or gstate.iround==0)):
						if gstate.players[plkey].ai == None:
							if display!=None:
								new_bet = ask_bet(pgame, gstate,plkey)
							else:
								new_bet = dummy_func(gstate.players,plkey,gstate.table)
						else:
							new_bet = gstate.players[plkey].choose_bet(gstate.players, gstate.table)
					if new_bet>np.amax(gstate.table.roundvals):
						RoundRecord.append(gstate.players[plkey].ID)
					gstate.make_bet(plkey, new_bet)
					bet_round=True
					print('%s bets : '%plkey, new_bet, ' for a total of ', gstate.table.roundvals[plind], 'this round.')
				#the last player to take aggressive action by a bet or raise is the first to show the hand
				#hence we need a record of who has raised last in each round
				if not gstate.players[plkey].fold:
					round_val = np.amax(gstate.table.roundvals)
				
			
			gstate.update_players()
			gstate.next_round()
			if gstate.iround>=gstate.nplayers and bet_round or gstate.inplayers==0:
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
		print('Players remaining in this hand: ', gstate.betplayers, gstate.inplayers)

		gstate.add_record(RoundRecord)

"""
showdown
Convoluted and unecessarily complicated right now... need to check all this
In: Players, table, betting order (not used atm, for the reveal if needed)

"""
def showdown(pgame, gstate, gtype=None):
	if gtype=='manual':
		get_final_hands(deck, players, dealer)
	
	playing_hands_name={}
	playing_hands = {}
	playing_values = {}
	max_hand_val =0
	for plkey in gstate.players:
		if not gstate.players[plkey].fold:
			tot_hand = gstate.players[plkey].hand + gstate.table.hand
			playing_hands[plkey], playing_values[plkey] = hand.full_hand_best(tot_hand, 5)
			playing_hands_name[plkey] = hand.poker_hand(playing_hands[plkey])
			
	for plkey in playing_hands:
		max_hand_val = max(max_hand_val, playing_values[plkey])

	win_inds = []

	for plkey in playing_hands:
		if playing_values[plkey]==max_hand_val:
			win_inds.append(gstate.players[plkey].order)

	
	gstate.payout(win_inds)
	payouts = gstate.table.payout(win_inds)
	
	for ipay in range(len(payouts)):
		for plkey in gstate.players:
			if gstate.players[plkey].order==ipay:
				print('\nWinnings for %s: %d'%(plkey, payouts[ipay]))
				print('Hand: ', gstate.players[plkey].hand)
				print('Table hand: ', gstate.table.hand)
				if plkey in playing_hands:
					print('Best type: ', playing_hands_name[plkey])
					print('Best hand: ', playing_hands[plkey])
		
	
	px = pgame.screen.get_rect().width/2

	sch = pgame.screen.get_rect().height
	py_mid = sch/2
	py = np.linspace(-0.3,0.3, gstate.inplayers)

	pgame.screen.fill((0,0,0))

	ipy=0
	for plkey in gstate.players:
		if gstate.players[plkey].betting:
			if plkey in playing_hands_name:
				hand_name = playing_hands_name[plkey]
			else:
				hand_name = 'fold'
			win_text= pgame.fontObj.render("Player {0.ID} ({1}): {2}".format(gstate.players[plkey], playing_hands_name[plkey],payouts[gstate.players[plkey].order] ), 1, (255,0,0))
			win_rect = win_text.get_rect()
			win_rect.center = (px, py_mid+py[ipy]*sch)
			print(win_rect.center, px, sch)
			pgame.screen.blit(win_text, win_rect)
			print('Blitting: ', plkey)
			ipy+=1
			
	pygame.display.flip()
	time.sleep(5)
	
	new_tot=0
	for plkey in gstate.players:
		new_tot+=gstate.players[plkey].bank

	if new_tot!=400*gstate.nplayers:
		print('Bank discrepancy')
		sys.exit()


	print(playing_hands)
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
	def __init__(self, screen, items, gamefontObj,bg_color=BLACK):
		self.screen = screen
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
 
	def set_mouse_visibility(self):
		if self.mouse_is_visible:
			pygame.mouse.set_visible(True)
		else:
			pygame.mouse.set_visible(False)

	def set_keyboard_selection(self, key):
		for item in self.items:
			# Return all to neutral
			item.set_italic(False)
			item.set_font_color(WHITE)

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
 
	def set_mouse_selection(self, item, mpos):
		if item.is_mouse_selection(mpos):
			item.set_font_color(RED)
			item.set_italic(True)
		else:
			item.set_font_color(WHITE)
			item.set_italic(False)

	def run(self, state, nplayers,chips0, blinds, gstate=None):
		mainloop = True
		prev_state=-1
		while mainloop:

			#State=0 --> init game
			#State=1 --> deal
			#State=2 --> play, blind
			update_flag=False
			
			if state==0 or gstate==None:
				rect_list = []
				#Assign players to list
				gstate = GameState(self.scr_width, self.scr_height, nplayers,chips0, blinds, self.fontObj)
				state=1
			elif gstate.state==1:
				gstate.move_dealer(gstate.dealer+1)
				#self.screen.blit(mbg, (CENTER[0]-SCW/2,CENTER[1]-SCH/2))
				gstate.new_hand()
			elif gstate.state==2:
				std_round(self, gstate, blind_round=True, display = self.screen)
				gstate.new_state(3)
			elif gstate.state==3:
				gstate.flop()
				std_round(self, gstate, blind_round=False, display = self.screen)
				gstate.new_state(4)
			elif gstate.state==4:
				gstate.turn()
				std_round(self, gstate, blind_round=False, display = self.screen)
				gstate.new_state(5)
			elif gstate.state==5:
				gstate.river()
				std_round(self, gstate, blind_round=False, display = self.screen)
				showdown(self, gstate)
				gstate.eliminate_players()
				if gstate.inplayers>1:
					gstate.new_state(1)
				else:
					gstate.new_state(6)
			elif gstate.state==6:
				winner_screen(self, gstate)
				return gstate, 'menu'
			else:
				print('Game state error.')
				sys.exit()

			if gstate.state!=prev_state:
				update_flag = True
			else:
				update_flag = False
			prev_state=gstate.state

			pressed = pygame.key.get_pressed()
			if pressed[pygame.K_SPACE]:
				return gstate, 'pausemenu'
				
			# Limit frame speed to 50 FPS
			self.clock.tick(50)

			"""mpos = pygame.mouse.get_pos()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					mainloop = False
				if event.type == pygame.KEYDOWN:
					self.mouse_is_visible = False
					self.set_keyboard_selection(event.key)
				if event.type == pygame.MOUSEBUTTONDOWN:
					for item in self.items:
						if item.is_mouse_selection(mpos):
							item.response()
 			"""
			if pygame.mouse.get_rel() != (0, 0):
				self.mouse_is_visible = True
				self.cur_item = None
 
			self.set_mouse_visibility()

			for item in self.items:
				if self.mouse_is_visible:
					self.set_mouse_selection(item, mpos)
				self.screen.blit(item.label, item.position)
	

			if update_flag:
				# Redraw the background
				self.screen.fill(self.bg_color)
				gstate.update_all(self.screen)

			
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
 
