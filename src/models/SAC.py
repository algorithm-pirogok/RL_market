# template for SAC
import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Normal

class Critic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()        

        self.state_dim = state_dim
        self.action_dim = action_dim

        self.network = nn.Sequential(
            nn.Linear(self.state_dim + self.action_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def get_qvalues(self, states, actions):
        '''
        input:
            states - tensor, (batch_size x features)
            actions - tensor, (batch_size x actions_dim)
        output:
            qvalues - tensor, critic estimation, (batch_size)
        '''
        # print("states:", states.shape)
        # print("actions:", actions.shape)
        qvalues = self.network(torch.cat([states.squeeze(), actions.squeeze()], dim=1)).squeeze()

        assert len(qvalues.shape) == 1 and qvalues.shape[0] == states.shape[0]
        
        return qvalues


class SAC_Actor(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()

        self.state_dim = state_dim
        self.action_dim = action_dim

        self.m = -20
        self.M = 2

        self.network = nn.Sequential(
            nn.Linear(self.state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 2*self.action_dim)
        )
    
    def apply(self, states):
        '''
        For given batch of states samples actions and also returns its log prob.
        input:
            states - PyTorch tensor, (batch_size x features)
        output:
            actions - PyTorch tensor, (batch_size x action_dim)
            log_prob - PyTorch tensor, (batch_size)
        '''
        network_output = self.network(states)
        means = network_output[:, :self.action_dim]
        variance = network_output[:, self.action_dim:]
        variance = torch.exp(self.m + 0.5*(self.M-self.m)*(torch.tanh(variance)+1))

        distr = Normal(means, variance)
        batch = distr.rsample()
        actions = torch.tanh(batch)
        log_prob = distr.log_prob(batch).sum(dim=-1, keepdim=True).squeeze()
        log_prob -= torch.log(1 - actions.pow(2) + 2e-6).sum(dim=1, keepdim=True).squeeze()

        return actions, log_prob  

    def get_action(self, states):
        '''
        Used to interact with environment by sampling actions from policy
        input:
            states - numpy, (batch_size x features)
        output:
            actions - numpy, (batch_size x actions_dim)
        '''
        # no gradient computation is required here since we will use this only for interaction
        with torch.no_grad():
            
            # hint: you can use `apply` method here
            if states.dim() > 1:
                actions = self.apply(states)[0].cpu().numpy()
            else:
                actions = self.apply(states.reshape(1, *states.shape))[0].cpu().numpy()
            assert isinstance(actions, (list,np.ndarray)), "convert actions to numpy to send into env"
            assert actions.max() <= 1. and actions.min() >= -1, "actions must be in the range [-1, 1]"
            return actions