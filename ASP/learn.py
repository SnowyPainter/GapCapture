import tensorflow as tf
import numpy as np
import random
import stockdata

import matplotlib.pyplot as plt
import numpy as np
import os
import random
import math
from collections import deque
import pandas as pd
import tensorflow as tf
from pylab import plt, mpl
from tensorflow import keras
from tensorflow.keras.optimizers import RMSprop
from sklearn.metrics import accuracy_score
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_squared_error
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
from keras.layers import Dropout

class observation_space:
    def __init__(self, n):
        self.shape = (n,)
class action_space:
    def __init__(self, n):
        self.n = n
    def sample(self):
        return random.randint(0, self.n - 1)

class ASPEnvironment:
    def _to_data(self):
        mean, std = self.raw.mean(), self.raw.std()
        self.normalized_data = (self.raw - mean) / std
        
    def _determin_to_trade(self, bar, threshold):
        diff = self.normalized_data[self.symbols[0]+"_Price"].iloc[bar] - self.normalized_data[self.symbols[1]+"_Price"].iloc[bar]
        diff = (1 if diff < 0 else (2 if diff > 0 else 0)) if abs(diff) >= threshold else 0
        return diff
    
    def __init__(self, symbol1, symbol2, affective_symbol, start, end, interval):
        self.observation_space = observation_space(1)
        self.logprofit_daybefore = 48
        self.action_space = action_space(3)
        self.symbols = [symbol1, symbol2]
        self.affective_symbol = affective_symbol
        self.start = start 
        self.end = end
        self.interval = interval
        self.raw = stockdata.create_dataset(self.symbols, affective_symbol, start, end, interval)
        self._to_data()
        self.features = self.raw.columns
    
    def _get_state(self):
        return self.normalized_data[self.features].iloc[self.bar-1:self.bar]

    def get_last(self):
        return self.normalized_data[self.features].iloc[-1]
    def get_state(self, bar):
        return self.normalized_data[self.features].iloc[bar-1:bar]
    
    def reset(self):
        self.total_reward = 0
        self.bar = self.logprofit_daybefore + 1
        state = self.normalized_data[self.features].iloc[self.bar-1:self.bar]
        return state.values
    
    def append_raw(self, df):
        self.raw = pd.concat([self.raw, df])
        self._to_data()
        return df
        
    def step(self, action):
        correct = action == self._determin_to_trade(self.bar - 1, 0.2)
        reward = 1 if correct else 0
        state = self._get_state()
        
        log_profit = np.log(self.raw[self.affective_symbol + "_Price"].iloc[self.bar] / self.raw[self.affective_symbol + "_Price"].shift(self.logprofit_daybefore).iloc[self.bar])
        
        if log_profit < 0 and action == 0:
            reward += 0.4
        elif log_profit > 0.3 and action != 0:
            reward += 0.7
        elif log_profit > 0.2 and action != 0:
            reward += 0.5
        elif log_profit > 0.05 and action != 0:
            reward += 0.2
        elif log_profit > 0 and action == 0:
            reward = 0
        
        self.total_reward += reward
        
        if self.bar >= len(self.normalized_data):
            done = True
        else:
            done = False
        info = {}
        self.bar += 1
        
        return state.values, reward, done, info
    
class DQNAgent:
    def __init__(self, env, max_steps, batch_size):
        self.env = env
        self.max_steps = max_steps
        self.batch_size = batch_size
        self.state_size = env.observation_space.shape[0]
        self.action_size = env.action_space.n
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.learning_rate = 0.001
        self.model = self._build_model()
        
    def _build_model(self):
        model = Sequential()
        model.add(Dense(48, input_shape=(self.state_size, len(self.env.features)), activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        action = self.model.predict(state, verbose=0)[0, 0]
        return np.argmax(action)
    
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])
            target_f = self.model.predict(state, verbose=0)
            target_f[0][0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
    def learn(self, episodes):
        for e in range(episodes):
            state = self.env.reset()
            state = np.reshape(state, [1, self.state_size, len(self.env.features)])
            for time in range(self.max_steps):
                action = self.act(state)
                next_state, reward, done, _ = self.env.step(action)
                if self.env.bar == len(self.env.normalized_data):
                    done = True
                else:
                    next_state = np.reshape(next_state, [1, self.state_size, len(self.env.features)])
                    self.remember(state, action, reward, next_state, done)
                    state = next_state
                if done:
                    print(f"{e} : {self.env.total_reward}")
                    break
            if len(self.memory) > self.batch_size:
                self.replay(self.batch_size)
                
    def save(self, path):
        self.model.save(path)