# import

import pygame, sys, random
from pygame.locals import *

#initialise the pygame module
pygame.init()

REWARD=0
# move up, move down, stop
ACTIONS=np.array([0,0,0])
# y value for p1, y for p2, x for ball, y for ball, direction of ball
FEATURES=np.array([0,0,0,0,0])

window_width = 160
window_height = 210
ScoreBarHeight = 30

white = (255, 255, 255)
black = (0, 0, 0)

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

myFont = pygame.font.SysFont("Times New Roman", 20)

cpuScoreDisplay = myFont.render(str(cpuScore), 1, white)
playerScoreDisplay = myFont.render(str(playerScore), 1, white)
#gameloop
myarray = list()

gameExit = False

state_size=5
action_size=3
agent = DQNAgent(state_size, action_size)
batch_size = 32
EPISODES = 10


while not gameExit:

        player_hit = 0
        computer_hit = 0
        player_scored = 0
        computer_scored = 0

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
                    if event.key == pygame.K_w:
                            paddleC_change = - (paddle_speed)
                    if event.key == pygame.K_s:
                            paddleC_change = (paddle_speed)
        elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            paddleP_change = 0
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                            paddleC_change = 0
        

        # bounding box for the paddles
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



        # ball Collision
        if ball_x == paddleP_x:
            if ball_y >= paddleP_y and ball_y <= (paddleP_y + paddleP_h):
                    ball_x += 1
                    ball_xspeed *= -1
                    player_hit = 1

        if ball_x == paddleC_x:
            if ball_y >= paddleC_y and ball_y <= (paddleC_y + paddleP_h):
                    ball_x -= 1
                    ball_xspeed *= -1
                    computer_hit = 1
        #END Ball/Paddle Collision



        #Ball Out of Bounds

        #If Player Loses
        if (ball_x<0):
                ball_x = 0.5 * window_width
                ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
                ball_xspeed = 1
                ball_yspeed = random.randint(-3,3)
                cpuScore += 1
                computer_scored = 1

        #If CPU Loses
        if (ball_x>window_width):
                ball_x = 0.5 * window_width
                ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
                ball_xspeed = -1
                ball_yspeed = random.randint(-3,3)
                playerScore += 1
                player_scored = 1

        #END Ball Out of Bounds



        #Ball Vertical Limit
        if ball_y + ball_yspeed <= ScoreBarHeight - 1:
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
        cpuScoreDisplay = myFont.render(str(cpuScore), 1, white)
        playerScoreDisplay = myFont.render(str(playerScore), 1, white)
        gameDisplay.blit(cpuScoreDisplay, (window_width*3/4, ScoreBarHeight/2 - 10))
        gameDisplay.blit(playerScoreDisplay, (window_width/4, ScoreBarHeight/2 - 10))
        #END Update and Display Score

        #SOMEONE PLEASE CHECK THE FOLLWOING LINE FOR MEMORY LEAK
        myarray.append(pygame.surfarray.pixels2d(gameDisplay.copy()))

        clock.tick(30)

        if player_hit:
            print('player hit')
        if computer_hit:
            print('computer hit')
            REWARD+=1

        if player_scored:
            print('player scored')
            REWARD-=10
        if computer_scored:
            print('computer scored')
            REWARD+=10
