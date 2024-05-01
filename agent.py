import torch
import random
import numpy as np
from collections import deque # data struct to store memories
from snake_gameAI import SnakeGameAI, Direction, Point
from model import Linear_Qnet, QTrainer
from helper import plot

MAX_MEMORY = 100_000 # max 100k in memory
BATCH_SIZE = 1000
LR = 0.001 # learning rate alpha

class Agent:

    def __init__(self):
        # things to store from the get go
        self.n_games = 0
        self.epsilon = 0 # parameter to control the randomness
        self.gamma = 0.9 # discount rate bellman eqn (btw 0 and 1, less than 1)
        self.memory = deque(maxlen=MAX_MEMORY) # if we exceed memory it will remove elements from the left
        self.model = Linear_Qnet(11,256,3) # state size, hidden layers, and output
        self.trainer = QTrainer(model,lr = LR, gamma = self.gamma)
    
    # for training we create a state --> action --> predict --> compare
    def get_state(self,game):
        # we get 11 states:
        # danger straight, right, left,
        # direction left, right, up, down
        # food left, right, up, down
 
        head = game.snake[0]
        # points next to the head
        point_l = Point(head.x-20,head.y)
        point_r = Point(head.x+20,head.y)
        point_u = Point(head.x,head.y-20)
        point_d = Point(head.x,head.y+20)

        # get current direction (booleans)
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        # set up state list
        state = [
            # danger straight
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)) ,

            # danger right
            (dir_r and game.is_collision(point_d)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) ,

            # danger left
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_d and game.is_collision(point_r)) ,

            # move direction left, right, up, down
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # food location left, right, up, down
            game.food.x < game.head.x, # food is on the left
            game.food.x > game.head.x, # food is on the right
            game.food.y < game.head.y, # food is upwards
            game.food.y > game.head.y  # food is downwards
        ]

        # convert booleans to integers and return
        return np.array(state,dtype=int)

    def remember(self,state,action,reward,next_state,game_over):
        # Deque will make sure to pop left if MAX_MEMORY reached
        self.memory.append((state, action, reward,next_state, game_over))

    def train_long_memory(self):
        #this one trains with a tensor/batch
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory,BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory
        
        # train the batch
        states,actions,rewards,next_states,game_overs = zip(*mini_sample)
        self.trainer.train_step(states,actions,rewards,next_states,game_overs)


    def train_short_memory(self,state,action,reward,next_state,game_over):
        #train only current step really
        self.trainer.train_step(state,action,reward,next_state,game_over)

    def get_action(self,state):
        # random moves: tradeoff between exploration and exploitation
        self.epsilon = 80 - self.ngames # as no of game increase eps decreases (reduces randomness)
        final_move = [0,0,0]

        if random.randint(0,200) < self.epsilon: # the smaller eps gets, the less random moves we do
            # just a random index on the action [0,0,0]
            midx = random.randint(0,2)
            final_move[midx] = 1
        else:
            # predict move instead of just going random
            state0 = torch.tensor(state,dtype = torch.float)
            prediction = self.model(state0) # needs tensor as input
            midx = torch.argmax(prediction).item() # gets the idx with the max arg in the move/action
            final_move[midx] = 1

        return final_move

    # global fcn
    def train():
        # initialize stuff
        plot_scores = [] #list to keep track of scores and plot
        plot_mean_scores = []
        total_score = 0
        record = 0
        agent = Agent()
        game = SnakeGameAI()

        # start training loop
        while True:
            # get the old (current) state
            state_old = agent.get_state(game)

            # get the move/action based on current state
            final_move = agent.get_action(state_old)

            # perform move and get new state
            reward, game_over, score = game.play_step(final_move)
            state_new = agent.get_state(game)

            # train the short term memory
            agent.train_short_memory(state_old,final_move,reward,state_new,game_over)

            # remember on memory
            agent.remember(state_old,final_move,reward,state_new,game_over)

            # if game over
            if game_over:
                # train the long memory (experience replay)
                game.reset()
                agent.n_games += 1
                agent.train_long_memory()

                if score > record:
                    record = score
                    # TODO: save the model
                    agent.model.save()

                # print info
                print('Game',agent.n_games,'Score',score,'Record:',record)

                # plot
                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                plot(plot_scores,plot_mean_scores)



    if __name__ == '__main__':
        train()



