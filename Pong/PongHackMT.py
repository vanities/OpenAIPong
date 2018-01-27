# import

import pygame, sys
from pygame.locals import *

#initialise the pygame module
pygame.init()

# set up display size
windowDisplay = pygame.display.set_mode((300, 300))

#Title
pygame.display.set_caption("PongHackMT")

#gameloop
while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.update()
