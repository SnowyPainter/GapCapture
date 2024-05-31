import sys
sys.path.append('..')

import stockdata
import MarketGap.learn as learn
import MarketGap.backtest as backtest
import numpy as np
import matplotlib.pyplot as plt
import configparser

settings = "./nepes_asic_settings.ini"
config = configparser.ConfigParser()
config.read(settings)
symbol1 = str(config["SETTINGS"]["SYMBOL1"]) + "." + config["SETTINGS"]["SYMBOL1_TAG"]
symbol2 = str(config["SETTINGS"]["SYMBOL2"]) + "." + config["SETTINGS"]["SYMBOL2_TAG"]
print(symbol1, symbol2)
env = learn.MarketEnvironment(symbol1, symbol2, stockdata.today_before(50), stockdata.today(),"5m")

amount = 100000000
stgy = backtest.Strategy1(env, amount, 0.0025, config["MODEL"]["PATH"])
stgy.test()
print(stgy.net_wealths[-1] / amount)
plt.plot(stgy.net_wealths)
plt.show()