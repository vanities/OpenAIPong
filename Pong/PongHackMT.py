from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import numpy as np
import os
import ray
import time
import gym
import pygame, sys, random
from pygame.locals import *

# Define some hyperparameters.

# The number of hidden layer neurons.
H = 200
learning_rate = 1e-4
# Discount factor for reward.
gamma = 0.99
# The decay factor for RMSProp leaky sum of grad^2.
decay_rate = 0.99

# The input dimensionality: 80x80 grid.
D = 80 * 80


def sigmoid(x):
    # Sigmoid "squashing" function to interval [0, 1].
    return 1.0 / (1.0 + np.exp(-x))


def preprocess(img):
    """Preprocess 210x160x3 uint8 frame into 6400 (80x80) 1D float vector."""
    # Crop the image.
    img = img[35:195]
    # Downsample by factor of 2.
    img = img[::2, ::2, 0]
    # Erase background (background type 1).
    img[img == 144] = 0
    # Erase background (background type 2).
    img[img == 109] = 0
    # Set everything else (paddles, ball) to 1.
    img[img != 0] = 1
    return img.astype(np.float).ravel()


def discount_rewards(r):
    """take 1D float array of rewards and compute discounted reward"""
    discounted_r = np.zeros_like(r)
    running_add = 0
    for t in reversed(range(0, r.size)):
        # Reset the sum, since this was a game boundary (pong specific!).
        if r[t] != 0:
            running_add = 0
        running_add = running_add * gamma + r[t]
        discounted_r[t] = running_add
    return discounted_r


def policy_forward(x, model):
    h = np.dot(model["W1"], x)
    h[h < 0] = 0  # ReLU nonlinearity.
    logp = np.dot(model["W2"], h)
    p = sigmoid(logp)
    # Return probability of taking action 2, and hidden state.
    return p, h


def policy_backward(eph, epx, epdlogp, model):
    """backward pass. (eph is array of intermediate hidden states)"""
    dW2 = np.dot(eph.T, epdlogp).ravel()
    dh = np.outer(epdlogp, model["W2"])
    # Backprop relu.
    dh[eph <= 0] = 0
    dW1 = np.dot(dh.T, epx)
    return {"W1": dW1, "W2": dW2}


@ray.remote
class PongEnv(object):
    def __init__(self):
        # Tell numpy to only use one core. If we don't do this, each actor may
        # try to use all of the cores and the resulting contention may result
        # in no speedup over the serial version. Note that if numpy is using
        # OpenBLAS, then you need to set OPENBLAS_NUM_THREADS=1, and you
        # probably need to do it from the command line (so it happens before
        # numpy is imported).
        os.environ["MKL_NUM_THREADS"] = "1"
        self.env = gym.make("Pong-v0")

    def compute_gradient(self, model):
        # Reset the game.
        observation = self.env.reset()
        # Note that prev_x is used in computing the difference frame.
        prev_x = None
        xs, hs, dlogps, drs = [], [], [], []
        reward_sum = 0
        done = False
        while not done:
            cur_x = preprocess(observation)
            x = cur_x - prev_x if prev_x is not None else np.zeros(D)
            prev_x = cur_x

            aprob, h = policy_forward(x, model)
            # Sample an action.
            action = 2 if np.random.uniform() < aprob else 3

            # The observation.
            xs.append(x)
            # The hidden state.
            hs.append(h)
            y = 1 if action == 2 else 0  # A "fake label".
            # The gradient that encourages the action that was taken to be
            # taken (see http://cs231n.github.io/neural-networks-2/#losses if
            # confused).
            dlogps.append(y - aprob)

            observation, reward, done, info = self.env.step(action)
            reward_sum += reward

            # Record reward (has to be done after we call step() to get reward
            # for previous action).
            drs.append(reward)

        epx = np.vstack(xs)
        eph = np.vstack(hs)
        epdlogp = np.vstack(dlogps)
        epr = np.vstack(drs)
        # Reset the array memory.
        xs, hs, dlogps, drs = [], [], [], []

        # Compute the discounted reward backward through time.
        discounted_epr = discount_rewards(epr)
        # Standardize the rewards to be unit normal (helps control the gradient
        # estimator variance).
        discounted_epr -= np.mean(discounted_epr)
        discounted_epr /= np.std(discounted_epr)
        # Modulate the gradient with advantage (the policy gradient magic
        # happens right here).
        epdlogp *= discounted_epr
        return policy_backward(eph, epx, epdlogp, model), reward_sum


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train an RL agent on Pong.")
    parser.add_argument("--batch-size", default=10, type=int,
                        help="The number of rollouts to do per batch.")
    parser.add_argument("--redis-address", default=None, type=str,
                        help="The Redis address of the cluster.")
    parser.add_argument("--iterations", default=-1, type=int,
                        help="The number of model updates to perform. By "
                             "default, training will not terminate.")
    args = parser.parse_args()
    batch_size = args.batch_size

    ray.init(redis_address=args.redis_address, redirect_output=True)

    # Run the reinforcement learning.

    running_reward = None
    batch_num = 1
    model = {}
    # "Xavier" initialization.
    model["W1"] = np.random.randn(H, D) / np.sqrt(D)
    model["W2"] = np.random.randn(H) / np.sqrt(H)
    # Update buffers that add up gradients over a batch.
    grad_buffer = {k: np.zeros_like(v) for k, v in model.items()}
    # Update the rmsprop memory.
    rmsprop_cache = {k: np.zeros_like(v) for k, v in model.items()}
    actors = [PongEnv.remote() for _ in range(batch_size)]
    iteration = 0
    while iteration != args.iterations:
        iteration += 1
        model_id = ray.put(model)
        actions = []
        # Launch tasks to compute gradients from multiple rollouts in parallel.
        start_time = time.time()
        for i in range(batch_size):
            action_id = actors[i].compute_gradient.remote(model_id)
            actions.append(action_id)
        for i in range(batch_size):
            action_id, actions = ray.wait(actions)
            grad, reward_sum = ray.get(action_id[0])
            # Accumulate the gradient over batch.
            for k in model:
                grad_buffer[k] += grad[k]
            running_reward = (reward_sum if running_reward is None
                              else running_reward * 0.99 + reward_sum * 0.01)
        end_time = time.time()
        print("Batch {} computed {} rollouts in {} seconds, "
              "running mean is {}".format(batch_num, batch_size,
                                          end_time - start_time,
                                          running_reward))
        for k, v in model.items():
            g = grad_buffer[k]
            rmsprop_cache[k] = (decay_rate * rmsprop_cache[k] +
                                (1 - decay_rate) * g ** 2)
            model[k] += learning_rate * g / (np.sqrt(rmsprop_cache[k]) + 1e-5)
            # Reset the batch gradient buffer.
            grad_buffer[k] = np.zeros_like(v)
batch_num += 1

#initialise the pygame module


window_width = 160
window_height = 210
ScoreBarHeight = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# set up display size
windowDisplay = pygame.display.set_mode((window_width,window_height), HWSURFACE | DOUBLEBUF | RESIZABLE)

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

gameDisplay = pygame.display.set_mode((window_width, window_height), HWSURFACE | DOUBLEBUF | RESIZABLE)

def paddle1(paddleP_x,paddleP_y):
        gameDisplay.blit(paddle1_img, (paddleP_x, paddleP_y))
def paddle2(paddleC_x,paddleC_y):
        gameDisplay.blit(paddle2_img, (paddleC_x, paddleC_y))
def ball(ball_x,ball_y):
        gameDisplay.blit(ball_img, (ball_x, ball_y))
paddleC_x = window_width - 10
paddleP_x = 10
paddleP_y = (0.5 * (window_height - ScoreBarHeight)) + ScoreBarHeight
paddleC_y = paddleP_y
paddleP_change = 0
paddleC_change = 0
paddle_speed = 2
ball_x = 0.5 * window_width
ball_y = (0.5 * (window_height - ScoreBarHeight)) + ScoreBarHeight
ball_xspeed = 1
ball_yspeed = random.randint(-3, 3)

#score text
playerScore = 0
cpuScore = 0
myFont = pygame.font.SysFont("Times New Roman", 20)
cpuScoreDisplay = myFont.render(str(cpuScore), 1, WHITE)
playerScoreDisplay = myFont.render(str(playerScore), 1, WHITE) # there was a / here??

#gameloop
myarray = list()
data = pygame.surfarray.array3d(gameDisplay)

while True:
        pygame.init()
        scoresLine = pygame.draw.rect(gameDisplay, WHITE, (0, 29, 160, 2), 0)
        pygame.display.update()

        while ball_yspeed == 0:
                ball_yspeed = random.randint(-3, 3)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        #Paddle Movement
        if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                            paddleP_change = -(paddle_speed)
                    if event.key == pygame.K_DOWN:
                            paddleP_change = (paddle_speed)
        if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                            paddleC_change = -(paddle_speed)
                    if event.key == pygame.K_s:
                            paddleC_change = (paddle_speed)
        elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            paddleP_change = 0
                    elif event.key == pygame.K_w or event.key == pygame.K_s:
                            paddleC_change = 0
        if paddleP_y + (paddleP_change + paddleP_h) >= window_height or paddleP_y + (paddleP_change) <= ScoreBarHeight:
                paddleP_change = 0
        if paddleC_y + (paddleC_change+paddleC_h) >= window_height or paddleC_y + (paddleC_change) <= ScoreBarHeight:
                paddleC_change = 0
        #END Paddle Movement


        #Ball Movement
        paddleP_y += paddleP_change
        paddleC_y += paddleC_change
        ball_x += ball_xspeed
        pygame.display.update()
        gameDisplay.fill(BLACK)
        paddle1(paddleP_x, paddleP_y)
        paddle2(paddleC_x, paddleC_y)
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
                ball_yspeed = random.randint(-3, 3)
                cpuScore += 1

        #If CPU Loses
        if (ball_x>window_width):
                ball_x = 0.5 * window_width
                ball_y = (0.5 * (window_height-ScoreBarHeight))+ScoreBarHeight
                ball_xspeed = -1
                ball_yspeed = random.randint(-3, 3)
                playerScore += 1

        #END Ball Out of Bounds

        #Ball Vertical Limit
        if ball_y + ball_yspeed <= ScoreBarHeight - 1:
                ball_y += (ScoreBarHeight - ball_y) - ball_yspeed
                ball_yspeed = -1 * ball_yspeed
        elif ball_y + ball_yspeed >= window_height:
                ball_y += (window_height - ball_y) - ball_yspeed
                ball_yspeed = -1 * ball_yspeed
        else:
                ball_y += ball_yspeed
        ball(ball_x, ball_y)
        #END Ball Vertical Limit

        #Update and Display Score
        cpuScoreDisplay = myFont.render(str(cpuScore), 1, WHITE)
        playerScoreDisplay = myFont.render(str(playerScore), 1, WHITE)
        gameDisplay.blit(cpuScoreDisplay, (window_width * 3/4, ScoreBarHeight/2 - 10))
        gameDisplay.blit(playerScoreDisplay, (window_width/4, ScoreBarHeight/2 - 10))
        #END Update and Display Score

        #SOMEONE PLEASE CHECK THE FOLLWOING LINE FOR MEMORY LEAK
        myarray.append(pygame.surfarray.pixels2d(gameDisplay.copy()))
        myarray.pop(0) # Clear first element

        clock.tick(30)

        if cpuScore == 10 or playerScore == 10:
            break

if cpuScore > playerScore:
    print("You LOST by", cpuScore - playerScore)
elif playerScore > cpuScore:
    print("You WON by", playerScore - cpuScore)
else:
    print("Close call, it was a tie!")
