# import

import pygame, sys, random
from pygame.locals import *

#initialise the pygame module
pygame.init()

window_width = 160
window_height = 210
ScoreBarHeight = 30

# set up display size
windowDisplay = pygame.display.set_mode((window_width,window_height))
#Title
pygame.display.set_caption("PongHackMT")

ball_height= 1
ball_width= 1
paddle1_height= 1
paddle1_width= 5
paddle2_height= 1
paddle2_width=5

black = (0, 0, 0)

clock = pygame.time.Clock()

ball_img = pygame.image.load('ball.png')
paddle1_img = pygame.image.load('paddle.png')
paddle2_img = pygame.image.load('paddle.png')
ball_img = pygame.image.load('ball.png')

gameDisplay = pygame.display.set_mode((window_width,window_height))

def paddle1(x1,y1):
        gameDisplay.blit(paddle1_img,(x1,y1))
def paddle2(x2,y2):
        gameDisplay.blit(paddle2_img,(x2,y2))
def ball(ball_x,ball_y):
        gameDisplay.blit(ball_img, (ball_x,ball_y))
x1 = window_width - 10
x2 = 10
y1 = (0.5*(window_height-ScoreBarHeight))+ScoreBarHeight
y2 = y1
y1_change = 0
y2_change = 0
paddle_speed = 1
ball_x = 0.5 * window_width
ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
ball_xspeed = 1
ball_yspeed = random.randint(-3,3)
#gameloop

gameExit = False
while not gameExit:
        while ball_yspeed == 0:
                ball_yspeed = random.randint(-3,3)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        #Paddle Movement    
        if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                            y1_change = - (paddle_speed)
                    if event.key == pygame.K_s:
                            y1_change = (paddle_speed)
        if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                            y2_change = - (paddle_speed)
                    if event.key == pygame.K_DOWN:
                            y2_change = (paddle_speed)
        if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                            y1_change = 0
        if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            y2_change = 0
        if y1 + (y1_change+9) >= window_height or y1 + (y1_change-9) <= ScoreBarHeight:
                y1_change = 0
        if y2 + (y2_change+9) >= window_height or y2 + (y2_change-9) <= ScoreBarHeight:
                y2_change = 0
        #END Paddle Movement

        
        #Ball Movement
        y1 += y1_change
        y2 += y2_change
        ball_x += ball_xspeed
        pygame.display.update()
        gameDisplay.fill(black)
        paddle1(x1,y1)
        paddle2(x2,y2)
        #END Ball Movement

        

        #Ball/Paddle Collision

        #END Ball/Paddle Collision



        #Ball Out of Bounds

        #END Ball Out of Bounds



        #Ball Vertical Limit
        if ball_y + ball_yspeed <= ScoreBarHeight:
                ball_y += (ScoreBarHeight-ball_y)-ball_yspeed
                ball_yspeed = -1* ball_yspeed
        elif ball_y + ball_yspeed >= window_height:
                ball_y += (window_height-ball_y)-ball_yspeed
                ball_yspeed = -1* ball_yspeed
        else:
                ball_y += ball_yspeed
        ball(ball_x,ball_y)
        #END Ball Vertical Limit



        #Update and Display Score

        #END Update and Display Score


        clock.tick(15)
