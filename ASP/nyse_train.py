import sys
sys.path.append('..')

import stockdata
import learn
import readini
import os

config = readini.read("./nvda_amd_settings.ini")
symbol1 = config["CODE1"]
symbol2 = config["CODE2"]
affective = config["AFFECTIVE"]
env = learn.ASPEnvironment(symbol1, symbol2, affective, stockdata.today_before(50), stockdata.today(), "5m")
agent = learn.DQNAgent(env, 10000, 64)
agent.learn(50)

if not os.path.exists('models'):
    os.makedirs('models')

agent.save(f"./models/{symbol1[:6]}{symbol2[:6]}.keras")