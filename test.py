#!/usr/bin/python

import wiiboard
import pygame
import time
import os, math, random, sys
from ConfigParser import ConfigParser
import csv


class WeightSprite(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.weight = 0.0
		self.update()

	def update(self):
		global screen_res, sys_font_weight_fgcolour, sys_font_weight, screen_res

		#if self.weight > 2:
		if True:
			self.text = "%.2f" % self.weight
		# else:
		#	self.text = "_.__"
		#	print "LESS THAN 2:", `self.weight`
		#while len(self.text) < 4:
		#	self.text = "0" + self.text

		self.image = sys_font_weight.render(self.text, True, sys_font_weight_fgcolour)

		self.rect = self.image.get_rect()
		self.rect.bottomright = screen_res


if True:

#def main():
	
	board = wiiboard.Wiiboard()

	system_file = "system.ini"
	sconf = ConfigParser()
	sconf.read(system_file)


	xdisplay = sconf.get("display", "xdisplay")
	if len(xdisplay) > 1:
		# using alternate display.
		print "Attempting to use device", xdisplay, "instead of the default."
		os.putenv("DISPLAY", xdisplay)



	pygame.init()
	sys_font_weight = pygame.font.SysFont(sconf.get("font_weight", "face"), int(sconf.get("font_weight", "size")))

	sys_font_weight.set_italic(False)
	sys_font_weight.set_underline(False)

	bgcolour = (0, 0, 0)
	sys_font_weight_fgcolour = (255, 255, 255)
	screen_res = (int(sconf.get("display", "width")), int(sconf.get("display", "height")))
	refresh_delay = int(sconf.get("display", "refresh_delay"))

	screen_options = 0
	if int(sconf.get("display", "fullscreen")) >= 1 and len(xdisplay) <= 1:
		screen_options = screen_options | pygame.fullscreen

	if int(sconf.get("display", "double_buffers")) >= 1:
		screen_options = screen_options | pygame.DOUBLEBUF

	if int(sconf.get("display", "hardware_surface")) >= 1:
		screen_options = screen_options | pygame.HWSURFACE

	if int(sconf.get("display", "opengl")) >= 1:
		screen_options = screen_options | pygame.opengl

	screen = pygame.display.set_mode(screen_res, screen_options)
	pygame.display.set_caption("scales application")

	weight_sprite = WeightSprite()
	weight_sprite.weight = 40.33
	frame = 0

	address = board.discover()
	board.connect(address) 

	time.sleep(0.1)
	board.setLight(True)
	done = False
	initialTime = time.time()

	c = csv.writer(open("Dados.csv","wb"))
	c.writerow ([ "X", "Y", "Peso", "Tempo"])



	while (not done):
		
		for event in pygame.event.get():
			if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE):
				done = True
			if event.type == wiiboard.WIIBOARD_MASS:
	
					print "Peso: " + `event.mass.totalWeight`
					#print "TR: " + `event.mass.topRight` + " BR: " + `event.mass.bottomRight` + " TL: " + `event.mass.topLeft` + " BL: " + `event.mass.bottomLeft`
					weight_sprite.weight = event.mass.totalWeight
					timeVar = event.mass.timeVar

					#Centro de massa
					comprimento = 433 #mm
					largura = 228 #mm
					copX = (comprimento/2)*((event.mass.topRight+event.mass.bottomRight)-(event.mass.topLeft+event.mass.bottomLeft))
					copX = copX / (event.mass.topRight+event.mass.bottomRight+event.mass.topLeft+event.mass.bottomLeft)
					copY = (largura/2)*((event.mass.topRight+event.mass.topLeft)-(event.mass.bottomRight+event.mass.bottomLeft))
					copY = copY / (event.mass.topRight+event.mass.bottomRight+event.mass.topLeft+event.mass.bottomLeft)
					peso = event.mass.topRight + event.mass.bottomRight + event.mass.topLeft + event.mass.bottomLeft
					tempo = time.time()-initialTime

					c.writerow([copX, copY, peso, tempo])

					try:
						if event.mass.totalWeight < 5:
							x1 = 0.
							x2 = 0.
							y1 = 0.
							y2 = 0.
						else:
							x1 = (float(event.mass.topLeft + event.mass.bottomLeft) / float(event.mass.totalWeight* 2))
							x2 = (float(event.mass.topRight + event.mass.bottomRight) / float(event.mass.totalWeight * 2))
							y1 = (float(event.mass.topRight + event.mass.topLeft) / float(event.mass.totalWeight * 2))
							y2 = (float(event.mass.bottomRight + event.mass.bottomLeft) / float(event.mass.totalWeight * 2))
					except:
							x1 = 0.
							x2 = 0.
							y1 = 0.
							y2 = 0.

					screen.fill(bgcolour) # blank

					x0 = screen_res[0]/2
					y0 = screen_res[1]/2

				
				#Linhas
				#	pygame.draw.line(screen, (0,0,255), (screen_res[0]/2,0), (screen_res[0]/2,screen_res[1]), 2)
				#	pygame.draw.line(screen, (0,0,255), (0,screen_res[1]/2), (screen_res[0],screen_res[1]/2), 2)

					weight_sprite.update()

					screen.blit(weight_sprite.image, weight_sprite.rect)

					xpos1 = (x1 * (screen_res[0]/2)) + (screen_res[0]/2)
					ypos1 = (y1 * (screen_res[1]/2)) + (screen_res[1]/2)
					pygame.draw.circle(screen, (255,0,0), (int(xpos1), y0), 20)
					pygame.draw.circle(screen, (255,0,0), (x0, int(ypos1)), 20)
					xpos2 = -(x2 * (screen_res[0]/2)) + (screen_res[0]/2)
					ypos2 = -(y2 * (screen_res[1]/2)) + (screen_res[1]/2)
					pygame.draw.circle(screen, (255,0,0), (int(xpos2), y0), 20)
					pygame.draw.circle(screen, (255,0,0), (x0, int(ypos2)), 20)


					pygame.draw.polygon(screen, (0,0,255), ( (int(xpos1), y0), (x0, int(ypos1)), (int(xpos2), y0), (x0, int(ypos2))), 2 )


					pygame.display.flip()
					pygame.time.wait(refresh_delay)


			elif event.type == wiiboard.WIIBOARD_BUTTON_PRESS:
				print "Button pressed!"

			elif event.type == wiiboard.WIIBOARD_BUTTON_RELEASE:
				print "Button released"
				#done = True

			#Other event types:
			#wiiboard.WIIBOARD_CONNECTED
			#wiiboard.WIIBOARD_DISCONNECTED

	board.disconnect()
	pygame.quit()
	sys.exit(0)
"""
#Run the script if executed
if __name__ == "__main__":
	main()
"""
