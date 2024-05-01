import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_Qnet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__() # cool new thing on python 3 that helps other classes use this one
        self.linear1 = nn.Linear(input_size,hidden_size) # applies linear transformation
        self.linear2 = nn.Linear(hidden_size,output_size) # applies lienar transformation
    
    def forward(self,x): # self.model() runs this fwd fcn so its some standard from pytorch
        x = F.relu(self.linear1(x)) # converts linear input into activation fcn value max(0,x) 
        x = self.linear2(x)
        return x
    
    def save(self,file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path,file_name)
        torch.save(self.state_dict(),file_name)

class QTrainer:
    def __init__(self,model,lr,gamma):
        self.lr = lr
        self.model = model
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(),lr = self.lr) # 1st order gradient-based optimization of stochastic fcns
        self.criterion = nn.MSELoss() # mean squared error

    def train_step(self,state,action,reward,next_state,game_over):
        state = torch.tensor(state,dtype = torch.float)
        action = torch.tensor(action,dtype = torch.long)
        reward = torch.tensor(reward,dtype = torch.float)
        next_state = torch.tensor(next_state,dtype = torch.float)
        # no need to do it for game over because its not even a tensor (0/1 only)

        if len(state.shape) == 1: # we only have one number
            # we want it was (1,x)... when you have multiple rows you already have it as a (n,x) size
            state = torch.unsqueeze(state,0)
            action = torch.unsqueeze(action,0)
            reward = torch.unsqueeze(reward,0)
            next_state = torch.unsqueeze(next_state,0)
            game_over = (game_over, )

        # 1. we want to get the predicted Q with current state
        # Q = model.predict(state0)
        pred = self.model(state)
        
        # 2. we want to get the new Q given the new state
        # Qnew = reward + gamma * max(Q(state1))
        # and we want to update the prediction with this new Q
        # only do this if not game over yet
        target = pred.clone()
        for idx in range(len(game_over)):
            Q_new = reward[idx] # initialize Q new as just the reward value
            if not game_over[idx]: # if on that given row it is not game over yet
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            # upate the prediction with the new target
            # the idea is that:
            # 1. you get the index of where your action had a 1, so if [0,0,1], the index is 2
            # 2. you update the value of Q on that index with the new Q
            # so if for example you had a [0,1,0] action with a Q of [3,2,1]
            # and your Q_new was like 4, then it updates to [3,4,1]
            target[idx][torch.argmax(action).item()] = Q_new #update the working row and the action 1 idx
        
        # 3. initialize and calcualte the loss gradient
        self.optimizer.zero_grad()
        loss = self.criterion(target,pred)
        loss.backward() # backward propagation

        self.optimizer.step() # move 1 step on that adam optimizer

            