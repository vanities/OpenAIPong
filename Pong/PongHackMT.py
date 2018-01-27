# import

import pygame, sys
from pygame.locals import *

WINDOW_HEIGHT = 210
WINDOW_WIDTH = 160

#initialise the pygame module
pygame.init()

# set up display size
windowDisplay = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

#Title
pygame.display.set_caption("PongHackMT")

#gameloop
while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.update()
