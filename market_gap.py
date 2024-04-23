import stockdata, learn
import backtest
import numpy as np
import matplotlib.pyplot as plt

tickers = ["nvda", "000660.KS"]
env = learn.MarketEnvironment("nvda", "000660.KS", stockdata.today_before(180), stockdata.today(),"1d")

def reshape(state):
    return np.reshape(state, [1, 1, 2])

def learn():
    agent = learn.DQNAgent(env, 10000, 64)
    agent.learn(30)
    agent.save("./nvdask.keras")

def bt():
    amount = 10000
    stgy = backtest.Strategy1(env, amount, 0.005)
    stgy.test()
    print(stgy.net_wealths[-1] / amount)
    plt.plot(stgy.net_wealths)
    plt.show()

bt()