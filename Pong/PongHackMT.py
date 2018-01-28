# import

import pygame, sys, random, math
from pygame.locals import *

import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

# for manual training
import csv

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)



#initialise the pygame module
pygame.init()

window_width = 500
window_height = 500
ScoreBarHeight = 30

white = (255, 255, 255)
black = (0, 0, 0)

# set up display size
windowDisplay = pygame.display.set_mode((window_width,window_height), HWSURFACE | DOUBLEBUF | RESIZABLE)
#Title
pygame.display.set_caption("PongHackMT")

ball_h = 9
ball_w = 9
paddleP_h = 45
paddleP_w = 15
paddleC_h = 45
paddleC_w = 15


clock = pygame.time.Clock()

ball_img = pygame.image.load('ball.png')
paddle1_img = pygame.image.load('paddle.png')
paddle2_img = pygame.image.load('paddle.png')

gameDisplay = pygame.display.set_mode((window_width,window_height), HWSURFACE | DOUBLEBUF | RESIZABLE)

def paddle1(paddleP_x,paddleP_y):
        gameDisplay.blit(paddle1_img,(paddleP_x,paddleP_y))
def paddle2(paddleC_x,paddleC_y):
        gameDisplay.blit(paddle2_img,(paddleC_x,paddleC_y))
def ball(ball_x,ball_y):
        gameDisplay.blit(ball_img, (ball_x,ball_y))


paddleC_x = window_width - 10 - paddleC_w
paddleP_x = 10
paddleP_y = (0.5*(window_height-ScoreBarHeight))+ScoreBarHeight
paddleC_y = paddleP_y
paddleP_change = 0
paddleC_change = 0
paddle_speed = window_height/105
ball_x = 0.5 * window_width
ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
ball_xspeed = window_width/160
ball_yspeed = random.uniform(-3,3)*window_height/210

#Score Vars
playerScore = 0
cpuScore = 0
playerTreat = 0
cpuTreat = 0
myFont = pygame.font.SysFont("Courier New", 20, bold=True)

def angleCalc(paddle_y, ball_y):
        y =  5* ( (ball_y - (paddle_y + (paddleC_h / 2 ))) / paddleC_h*.5 )
        return y


gameExit = False

state_size=8
action_size=3
agent = DQNAgent(state_size, action_size)
batch_size = 32
EPISODES = 10

REWARD=0
# move up, stop, move down
ACTIONS=np.array([0,0,0])
# player y
# change in player y
# opponent y
# change in opponent y
# ball x
# ball y
# change in ball x
# change in ball y
FEATURES=np.array([0,0,0,0,0,0,0,0])


myFile = open('mining.csv', 'a+')

while not gameExit:

        player_hit = 0
        computer_hit = 0
        player_scored = 0
        computer_scored = 0
        # scoresLine = pygame.draw.rect(gameDisplay, white, (0, ScoreBarHeight-1, window_width, 2), 0)
        # scoresLine = pygame.draw.rect(gameDisplay, white, (0, 29, 160, 2), 0)
        pygame.display.update()
        playerTreat = 0
        cpuTreat = 0


        while ball_yspeed == 0:
                ball_yspeed = random.uniform(-3,3)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        state = np.array([paddleP_y,paddleP_change, paddleC_y, paddleC_change,
                                   ball_x, ball_y, ball_xspeed,  ball_yspeed])
        action = agent.act(state)

        if action == 0:
            paddleC_change = - (paddle_speed)
        # down
        if action == 2:
            paddleC_change = (paddle_speed)

        if ball_x<0:
            done = True
        else:
            done = False

        next_state, reward, done = (np.array([paddleP_y,paddleP_change, paddleC_y, paddleC_change,
                                   ball_x, ball_y, ball_xspeed,  ball_yspeed]), REWARD, done)
        next_state = np.reshape(next_state, [1, state_size])
        agent.remember(state, action, reward, next_state, done)
        state = next_state

        if done:
            print('Reward:', REWARD)
        #if len(agent.memory) > batch_size:
         #   agent.replay(batch_size)

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
        if paddleP_y + (paddleP_change+paddleP_h) >= window_height+paddle_speed or paddleP_y + (paddleP_change) <= ScoreBarHeight:
                paddleP_change = 0
        if paddleC_y + (paddleC_change+paddleC_h) >= window_height+paddle_speed or paddleC_y + (paddleC_change) <= ScoreBarHeight:
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

        #Player Paddle
        if ball_x + ball_xspeed <= paddleP_x + paddleP_w - 1 and ball_x + ball_w - 1 + ball_xspeed >= paddleP_x:
                if ball_y + ball_yspeed <= paddleP_y + paddleP_h - 1 and ball_y + ball_h - 1 + ball_yspeed >= paddleP_y:
                    ball_x +=1
                    ball_xspeed *= -1
                    angle = angleCalc(paddleP_y, ball_y)
                    ball_yspeed = ball_xspeed * math.sin(angle)*2
                    cpuTreat = 1
        #CPU paddle
        if ball_x + ball_xspeed <= paddleC_x + paddleC_w - 1 and ball_x + ball_w - 1 + ball_xspeed >= paddleC_x:
                if ball_y + ball_yspeed <= paddleC_y + paddleC_h - 1 and ball_y + ball_h - 1 + ball_yspeed >= paddleC_y:
                    ball_x -= 1
                    ball_xspeed *= -1
                    angle = angleCalc(paddleC_y, ball_y)
                    ball_yspeed = ball_xspeed * math.sin(angle) *-2
                    cpuTreat = 1

        # player_hit = 1
        #
        #        if ball_x == paddleC_x:
        #            if ball_y >= paddleC_y and ball_y <= (paddleC_y + paddleP_h):
        #                    ball_x -= 1
        #                    ball_xspeed *= -1
        #                    computer_hit = 1

        #END Ball/Paddle Collision



        #Ball Out of Bounds

        #If Player Loses
        if (ball_x<0):
                # reset
                ball_x = 0.5 * window_width
                ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
                #ball_xspeed *=
                ball_yspeed = random.uniform(-3,3)
                cpuScore += 1
                computer_scored = 1
                state = np.array([paddleP_y,paddleP_change, paddleC_y, paddleC_change,
                                   ball_x, ball_y, ball_xspeed,  ball_yspeed])

                state = np.reshape(state, [1, state_size])

        #If CPU Loses
        if (ball_x>window_width):
                ball_x = 0.5 * window_width
                ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
                #ball_xspeed = -1
                ball_yspeed = random.uniform(-3,3)
                playerScore += 1
                cpuTreat = -2


                cpuTreat = -2
        #When Score reaches 20
        if playerScore == 20 or cpuScore == 20:
                pygame.quit()
                sys.exit()
                
        #END Ball Out of Bounds
                player_scored = 1
                state = np.array([paddleP_y,paddleP_change, paddleC_y, paddleC_change,
                                   ball_x, ball_y, ball_xspeed,  ball_yspeed])

                state = np.reshape(state, [1, state_size])

        #END Ball Out of Bounds


        #Ball Vertical Limit
        if ball_y  + ball_yspeed <= ScoreBarHeight - 1:
                ball_y += (ScoreBarHeight-ball_y)-ball_yspeed
                ball_yspeed = -1* ball_yspeed
        elif ball_y + (ball_h-1) +ball_yspeed >= window_height:
                ball_y += (window_height-(ball_y+ball_h-1))-ball_yspeed
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

        clock.tick(60)

        if player_hit:
            print('player hit')
        if computer_hit:
            print('computer hit')
            REWARD+=1

        if player_scored:
            print('player scored')
            #REWARD-=10
        if computer_scored:
            print('computer scored')
            #REWARD+=10

        if myFile:
            writer = csv.writer(myFile)
            writer.writerows([{paddleP_y,paddleP_change, paddleC_y, paddleC_change,
                                   ball_x, ball_y, ball_xspeed,  ball_yspeed, reward}])


if gameExit:
    model.save('saved_model.h5')
    myFile.close()
