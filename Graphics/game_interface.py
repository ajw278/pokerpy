#!/usr/bin/python

"""
Notes:
"""
from __future__ import print_function


import pygame


class interface():
	def __init__(self, items):
		self.items = items



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
 
	def set_mouse_selection(self, item, mpos):
		"""Marks the MenuItem the mouse cursor hovers on."""
		if item.is_mouse_selection(mpos):
			item.set_font_color(RED)
			item.set_italic(True)
		else:
			item.set_font_color(WHITE)
			item.set_italic(False)

	def event_check(self):
		mpos = pygame.mouse.get_pos()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				mainloop = False
			if event.type == pygame.KEYDOWN:
				mouse_is_visible = False
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
			if mouse_is_visible:
				self.set_mouse_selection(item, mpos)

			self.screen.blit(item.label, item.position)

		pygame.display.flip()
