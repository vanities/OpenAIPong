# import

import pygame, sys, random
from pygame.locals import *

#initialise the pygame module
pygame.init()

window_width = 160
window_height = 210
ScoreBarHeight = 30

white = (255, 255, 255)

# set up display size
windowDisplay = pygame.display.set_mode((window_width,window_height))
#Title
pygame.display.set_caption("PongHackMT")

ball_height = 1
ball_width = 1
paddleP_h = 15
paddleP_w = 1
paddleC_h = 15
paddleC_w = 1

black = (0, 0, 0)

clock = pygame.time.Clock()

ball_img = pygame.image.load('ball.png')
paddle1_img = pygame.image.load('paddle.png')
paddle2_img = pygame.image.load('paddle.png')

gameDisplay = pygame.display.set_mode((window_width,window_height))

def paddle1(paddleP_x,paddleP_y):
        gameDisplay.blit(paddle1_img,(paddleP_x,paddleP_y))
def paddle2(paddleC_x,paddleC_y):
        gameDisplay.blit(paddle2_img,(paddleC_x,paddleC_y))
def ball(ball_x,ball_y):
        gameDisplay.blit(ball_img, (ball_x,ball_y))
paddleC_x = window_width - 10
paddleP_x = 10
paddleP_y = (0.5*(window_height-ScoreBarHeight))+ScoreBarHeight
paddleC_y = paddleP_y
paddleP_change = 0
paddleC_change = 0
paddle_speed = 2
ball_x = 0.5 * window_width
ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
ball_xspeed = 1
ball_yspeed = random.randint(-3,3)
#score text
playerScore = 0
cpuScore = 0

myFont = pygame.font.SysFont("none", 20)

randNumLabel = myFont.render(str(cpuScore), 1, white)
diceDisplay = myFont.render(str(playerScore), 1, white)
#gameloop
myarray = list()

gameExit = False
while not gameExit:

        scoresLine = pygame.draw.rect(gameDisplay, white, (0, 29, 160, 2), 0)
        pygame.display.update()

        while ball_yspeed == 0:
                ball_yspeed = random.randint(-3,3)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        #Paddle Movement
        if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                            paddleP_change = - (paddle_speed)
                    if event.key == pygame.K_DOWN:
                            paddleP_change = (paddle_speed)
        if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                            paddleC_change = - (paddle_speed)
                    if event.key == pygame.K_s:
                            paddleC_change = (paddle_speed)
        if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            paddleP_change = 0
        if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                            paddleC_change = 0
        if paddleP_y + (paddleP_change+paddleP_h) >= window_height or paddleP_y + (paddleP_change) <= ScoreBarHeight:
                paddleP_change = 0
        if paddleC_y + (paddleC_change+paddleC_h) >= window_height or paddleC_y + (paddleC_change) <= ScoreBarHeight:
                paddleC_change = 0
        #END Paddle Movement


        #Ball Movement
        paddleP_y += paddleP_change
        paddleC_y += paddleC_change
        ball_x += ball_xspeed
        pygame.display.update()
        gameDisplay.fill(black)
        paddle1(paddleP_x,paddleP_y)
        paddle2(paddleC_x,paddleC_y)
        #END Ball Movement



        #Ball/Paddle Collision
        if ball_x == paddleP_x:
            if ball_y >= paddleP_y and ball_y <= (paddleP_y + paddleP_h):
                    ball_x += 1
                    ball_xspeed *= -1
        if ball_x == paddleC_x:
            if ball_y >= paddleC_y and ball_y <= (paddleC_y + paddleP_h):
                    ball_x -= 1
                    ball_xspeed *= -1
        #END Ball/Paddle Collision



        #Ball Out of Bounds

        #If Player Loses
        if (ball_x<0):
                ball_x = 0.5 * window_width
                ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
                ball_xspeed = 1
                ball_yspeed = random.randint(-3,3)
                cpuScore += 1

        #If CPU Loses
        if (ball_x>window_width):
                ball_x = 0.5 * window_width
                ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
                ball_xspeed = -1
                ball_yspeed = random.randint(-3,3)
                playerScore += 1

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
        gameDisplay.blit(randNumLabel, (1, 5))
        gameDisplay.blit(diceDisplay, (45, 5))
        #END Update and Display Score

        #SOMEONE PLEASE CHECK THE FOLLWOING LINE FOR MEMORY LEAK
        myarray.append(pygame.surfarray.pixels2d(gameDisplay.copy()))

        clock.tick(15)
