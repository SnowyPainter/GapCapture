import sys
sys.path.append('..')

import stockdata
import StockPair.learn as learn
import StockPair.backtest as backtest
import numpy as np
import matplotlib.pyplot as plt
import configparser
import pandas as pd

settings = "./hanmi_sk_settings.ini"
config = configparser.ConfigParser()
config.read(settings)
symbol1 = str(config["SETTINGS"]["SYMBOL1"]) + "." + config["SETTINGS"]["SYMBOL1_TAG"]
symbol2 = str(config["SETTINGS"]["SYMBOL2"]) + "." + config["SETTINGS"]["SYMBOL2_TAG"]
env = learn.MarketEnvironment(symbol1, symbol2, stockdata.today_before(50), stockdata.today(),"5m")

amount = 100000000
stgy = backtest.Strategy1(env, amount, 0.0025, config["MODEL"]["PATH"])
stgy.test()
print(stgy.net_wealths[-1] / amount)

nvda = stockdata.create_dataset(["nvda"], stockdata.today_before(50), stockdata.today(),"5m")
df = pd.DataFrame({"NetWealth" : stgy.net_wealths, "Nvda" : nvda["nvda_Price"].iloc[len(nvda) - len(stgy.net_wealths):]})
df = stockdata.normalize(df)
plt.plot(df["NetWealth"], label = "Net Wealth")
plt.plot(df["Nvda"], label="Nvda")
plt.legend()
plt.show()