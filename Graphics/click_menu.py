#!/usr/bin/python
 
import sys
import pygame
import entry
import copy
import os
from collections import namedtuple
pygame.init()

from pygame.locals import *

scriptpath = os.path.dirname(os.path.realpath(__file__))
 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

KIND_DICT = {0: 'd', 1:'c',2:'h',3:'s'}
INV_KIND_DICT =  dict([[v,k] for k,v in KIND_DICT.items()])
VALUE_DICT = {0: 2, 1: 3, 2: 4, 3: 5, 4:6, 5:7,6:8,7:9,8:10,9:'j', 10:'q',11:'k',12:'a'}
INV_VALUE_DICT = dict([[v,k] for k,v in VALUE_DICT.items()])
PICTURE = ['j', 'q','k', 'a']
 

Card = namedtuple("Card", ["value", "kind"])


class MenuItem(pygame.font.Font):
	def __init__(self, text, font=None, font_size=30,  font_color=WHITE, pos=(0, 0)):
		pos_x, pos_y = pos[:]
		pygame.font.Font.__init__(self, font, font_size)
		self.text = text
		self.font_size = font_size
		self.font_color = font_color
		self.label = self.render(self.text, 1, self.font_color)
		self.width = self.label.get_rect().width
		self.height = self.label.get_rect().height
		self.dimensions = (self.width, self.height)
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.position = pos_x, pos_y
 
	def is_mouse_selection(self, pos):
		posx, posy = pos[:]
		if (posx >= self.pos_x and posx <= self.pos_x + self.width) and \
			(posy >= self.pos_y and posy <= self.pos_y + self.height):
			return True
		return False
 
	def set_position(self, x, y):
		self.position = (x, y)
		self.pos_x = x
		self.pos_y = y

	def set_font_color(self, rgb_tuple):
		self.font_color = rgb_tuple
		self.label = self.render(self.text, 1, self.font_color)
 
class GameMenu():
	def __init__(self, screen, items, bg_color=BLACK,bg_alpha=255, font=None, font_size=30, font_color=WHITE):
		self.screen = screen
		self.scr_width = self.screen.get_rect().width
		self.scr_height = self.screen.get_rect().height

		self.bg_color = bg_color
		self.bg_alpha = bg_alpha
		self.clock = pygame.time.Clock()

		self.items = []
		for index, item in enumerate(items):
			menu_item = MenuItem(item, font, font_size, font_color)

			# t_h: total height of text block
			t_h = len(items) * menu_item.height
			pos_x = (self.scr_width / 2) - (menu_item.width / 2)
			# This line includes a bug fix by Ariel (Thanks!)
			# Please check the comments section of pt. 2 for an explanation
			pos_y = (self.scr_height /2)-(t_h / 2)+ ((index*2)+index*menu_item.height)

			menu_item.set_position(pos_x, pos_y)
			self.items.append(menu_item)

		self.mouse_is_visible = True
		self.cur_item = None
 
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

		return None
 
	def set_mouse_selection(self, item, mpos):
		"""Marks the MenuItem the mouse cursor hovers on."""
		if item.is_mouse_selection(mpos):
			item.set_font_color(RED)
			item.set_italic(True)
		else:
			item.set_font_color(WHITE)
			item.set_italic(False)
 
	def run(self):
		mainloop = True
		while mainloop:
		    # Limit frame speed to 50 FPS
		    self.clock.tick(50)
	 
		    mpos = pygame.mouse.get_pos()
	 
		    for event in pygame.event.get():
		        if event.type == pygame.QUIT:
		            mainloop = False
		        if event.type == pygame.KEYDOWN:
		            self.mouse_is_visible = False
		            keyslct = self.set_keyboard_selection(event.key)
		            if keyslct!=None:
		            	return keyslct
		        if event.type == pygame.MOUSEBUTTONDOWN:
		            for item in self.items:
		                if item.is_mouse_selection(mpos):
		                    return item.text
	 
		    if pygame.mouse.get_rel() != (0, 0):
		        self.mouse_is_visible = True
		        self.cur_item = None
	 
		    self.set_mouse_visibility()
	 
		    # Redraw the background
		    pygame.Surface.convert_alpha(self.screen)
		    self.screen.fill(self.bg_color)
		    self.screen.set_alpha(self.bg_alpha)
	 
		    for item in self.items:
		        if self.mouse_is_visible:
		            self.set_mouse_selection(item, mpos)
		        self.screen.blit(item.label, item.position)
	 
		    pygame.display.flip()

class MiniGameMenu():
	def __init__(self, screen, items, bg_color=BLACK,bg_alpha=255, font=None, font_size=30, font_color=WHITE, loc=None, size=None):
		self.screen = screen
		if size==None:
			self.scr_width = self.screen.get_rect().width
			self.scr_height = self.screen.get_rect().height
			self.menu_surf = self.screen
		else:
			self.scr_width = size[0]
			self.scr_height = size[1]
			self.menu_surf = pygame.Surface((size[0], size[1]))

		if loc==None:
			self.xoffset = 0
			self.yoffset = 0
		else:
			self.xoffset = loc[0]
			self.yoffset = loc[1]
			
		self.bg_color = bg_color
		self.bg_alpha = bg_alpha
		self.clock = pygame.time.Clock()
	 
		self.items = []
		for index, item in enumerate(items):
		    menu_item = MenuItem(item, font, font_size, font_color)
	 
		    # t_h: total height of text block
		    t_h = len(items) * menu_item.height
		    pos_x = (self.scr_width / 2) - (menu_item.width / 2)+self.xoffset
		    # This line includes a bug fix by Ariel (Thanks!)
		    # Please check the comments section of pt. 2 for an explanation
		    pos_y = (self.scr_height /2)-(t_h / 2)+ ((index*2)+index*menu_item.height)+self.yoffset
	 
		    menu_item.set_position(pos_x, pos_y)
		    self.items.append(menu_item)
	 
		self.mouse_is_visible = True
		self.cur_item = None
 
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

		return None
 
	def set_mouse_selection(self, item, mpos):
		"""Marks the MenuItem the mouse cursor hovers on."""
		if item.is_mouse_selection(mpos):
			item.set_font_color(RED)
			item.set_italic(True)
		else:
			item.set_font_color(WHITE)
			item.set_italic(False)
 
	def run(self):
		mainloop = True
		while mainloop:
			# Limit frame speed to 50 FPS
			self.clock.tick(50)
	 
			mpos = pygame.mouse.get_pos()
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					mainloop = False
				if event.type == pygame.KEYDOWN:
					self.mouse_is_visible = False
					keyslct = self.set_keyboard_selection(event.key)
				if keyslct!=None:
					return keyslct
				if event.type == pygame.MOUSEBUTTONDOWN:
					for item in self.items:
						if item.is_mouse_selection(mpos):
							return item.text
							
			if pygame.mouse.get_rel() != (0, 0):
				self.mouse_is_visible = True
				self.cur_item = None

			self.set_mouse_visibility()
	 
			# Redraw the background


			pygame.Surface.convert_alpha(self.menu_surf)
			self.menu_surf.fill(self.bg_color)
			self.menu_surf.set_alpha(self.bg_alpha)

			self.screen.blit(self.menu_surf, (self.xoffset, self.yoffset))

			for item in self.items:
				if self.mouse_is_visible:
					self.set_mouse_selection(item, mpos)
					self.screen.blit(item.label, item.position)

			pygame.display.flip()


def get_text(screen, font,font_color=(255,0,0), restrict='all', maxlen=20, prompt_string='Enter: ', pgame=None, gstate=None):

	scw = screen.get_rect().width
	sch = screen.get_rect().height
	
	txtbx = entry.Input(maxlength=maxlen, color=font_color, x=int(float(scw)/2.), y=int(0.35*float(sch)), font=font, prompt=prompt_string)
	while True:
		# events for txtbx
		events = pygame.event.get()
		if not pgame==None:
			it_list = [v for v in gstate.graphics.pboxes.values()]+[gstate.graphics.tbox]
			ret_val = pgame.tick(it_list, events=events, gstate = gstate)
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


def get_cards(screen, ncards, deck, pgame=None, gstate=None): 
		icards=0 
		
		tmp_deck = copy.copy(deck)

		ret_cards = []
		fontObj = pygame.font.Font(scriptpath+'/Fonts/Alien_League.ttf', 20)
		orig_message = 'Enter card {0} (e.g. J-S = Jack of Spades): '
		message = orig_message
		while icards<ncards:
			card_str = None
			while type(card_str)!=str:
				card_str = get_text(screen, fontObj,prompt_string=message.format(icards+1), pgame=pgame, gstate=gstate)
			card_str = card_str.lower().replace(" ", "")
			str_split = card_str.split('-')
			if len(str_split)!=2:
				message = 'Check format. '+orig_message
			else:
				fail=False
				if not str_split[0] in PICTURE:
					try:
						value = INV_VALUE_DICT[int(str_split[0])]
					except:
						fail=True
					message = 'Value not recognised. '+orig_message
				else:
					value = INV_VALUE_DICT[str_split[0]]
						
				if not fail: 
					if not str_split[1] in INV_KIND_DICT:
						message = 'Kind not recognised. '+orig_message
					else:
						kind = INV_KIND_DICT[str_split[1]]
						incard = Card(value, kind)
						if not incard in tmp_deck:
							message = 'Card not in deck. '+orig_message
						else:
							message = orig_message
							ret_cards.append(incard)
							tmp_deck.remove(incard)
							icards+=1
							


		return ret_cards
	


 
if __name__ == "__main__":
    def hello_world():
        print ("Hello World!")
 
    # Creating the screen
    screen = pygame.display.set_mode((640, 480), 0, 32)
 
    menu_items = ('Start', 'Quit')
 
    pygame.display.set_caption('Game Menu')
    gm = GameMenu(screen, menu_items)
    result = gm.run()

    if result=='Start':
         hello_world()
    else:
         sys.exit()
 
