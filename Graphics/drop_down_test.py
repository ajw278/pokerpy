
import pygame


class PopupMenuItem():
	def __init__(self, text, font=None, font_size=30,
                 font_color=WHITE, (pos_x, pos_y)=(0, 0)):
 
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
 
	def is_mouse_selection(self, (posx, posy)):
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

class PopupMenu():
	def init(self, dims, options, loc=(0,0), font=None, font_size=30):
		self.popupSurf = pygame.Surface(dims[0], dims[1])
		self.position = loc
		self.dims = dims
		self.options = options
		self.items = []
		for opt in options:
			items.append(PopupMenuItems(opt, font=font, font_size=font_size)

	 def set_mouse_selection(self, mpos):
		"""Marks the MenuItem the mouse cursor hovers on."""
		for item in self.items:
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




	def 
			top = self.position[1]
			
			for i in range(len(self.options)):
				textSurf = BASICFONT.render(options[i], 1, BLUE)
				textRect = textSurf.get_rect()
				textRect.top = top
				textRect.left = self.position[0]
				top += pygame.font.Font.get_linesize(BASICFONT)
			popupSurf.blit(textSurf, textRect)
			popupRect = popupSurf.get_rect()
			popupRect.centerx = self.position[0]+self.dims[0]/2.
			popupRect.centery = self.position[1]+self.dims[1]/2.
			DISPLAYSURFACE.blit(popupSurf, popupRect)
			pygame.display.update()


	def run(self)
		while True:



if __name__ =='__main__':

	screen = pygame.display.set_mode((640, 480), 0, 32)

	pygame.display.set_caption('Game Menu')
	popup = make_popup()
	
