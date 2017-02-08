#!/usr/bin/python

"""
Notes:
- Not sure the right nplayers being used - need to check when players are knocked out
"""

import pygame
 
import sys
import pygame
import pokerpy
import im_objects
import player
import table
import random
 
pygame.init()
 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


class GameState():
	def __init__(self,scw, sch, nplayers,chips0, textfontObj):
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
		self.table = table_data
		self.tbox = dealer_box
		self.players = player_dict
		self.pboxes = box_dict
		self.dealer = random.randint(0, nplayers-1)
		self.state=1
		self.deck = pokerpy.init_deck()

	def move_dealer(self,iplayer):
		self.dealer = iplayer%self.table.nplayers

	def new_hand(self):
		self.deck = pokerpy.init_deck()
		self.table.new_hand()
		cardset, deck = pokerpy.init_deal(self.deck, self.table.nplayers)
		pokerpy.assign_hand(self.dealer, self.players, cardset)
		self.state=2

	
	def update_all(self, display_surface):
		print('Updating')	

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
		display_surface.blit(self.tbox.text, self.tbox.textloc)

		return None



"""
Items must now conform to the definition here
"""

class PokerGame():
	def __init__(self, screen, items, gamefont, bg_color=BLACK):
		self.screen = screen
		self.scr_width = self.screen.get_rect().width
		self.scr_height = self.screen.get_rect().height
		self.fontObj = gamefont
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

	def run(self, state, nplayers,chips0, gstate=None):
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
				gstate = GameState(self.scr_width, self.scr_height, nplayers,chips0, self.fontObj)
				state=1
			elif gstate.state==1:
				gstate.move_dealer(gstate.dealer+1)
				#self.screen.blit(mbg, (CENTER[0]-SCW/2,CENTER[1]-SCH/2))
				gstate.new_hand()
			elif gstate.state==2:
				#Do betting here
				rect_list=[]

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

			mpos = pygame.mouse.get_pos()
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
        print "Hello World!"
 
    # Creating the screen
    screen = pygame.display.set_mode((640, 480), 0, 32)
 
    menu_items = ('Start', 'Quit')
    funcs = {'Start': hello_world,
             'Quit': sys.exit}
 
    pygame.display.set_caption('Game Menu')
    gm = GameMenu(screen, menu_items)
    gm.run()
 
