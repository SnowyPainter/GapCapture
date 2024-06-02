import sys
sys.path.append('..')

import stockdata
import readini
import learn, backtest
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

settings = "./nvda_amd_settings.ini"
config = readini.read(settings)
symbol1 = str(config["CODE1"]) #+ "." + config["TAG1"]
symbol2 = str(config["CODE2"]) #+ "." + config["TAG2"]

env = learn.ASPEnvironment(symbol1, symbol2, config["AFFECTIVE"], stockdata.today_before(50), stockdata.today(),"5m")

amount = 100000000
stgy = backtest.Strategy1(env, amount, 0.0025, config["MODEL"])
stgy.run()
print(stgy.trades)
print("기여도", (stgy.affective_system_profit_sum / stgy.net_wealths[-1]))
print("End", (stgy.net_wealths[-1] - amount) / amount)
print("Best ", (max(stgy.net_wealths) - amount) / amount)
print("Worst ", (min(stgy.net_wealths) - amount) / amount)

df = pd.DataFrame({"NetWealth":stgy.net_wealths, f"{env.affective_symbol}": env.raw[f"{env.affective_symbol}_Price"].iloc[len(env.raw[f"{env.affective_symbol}_Price"]) - len(stgy.net_wealths):]})
mean, std = df.mean(), df.std()
df = (df-mean) / std

print(df.corr())

plt.plot(df["NetWealth"], label="Net Wealth")
plt.plot(df[f"{env.affective_symbol}"], label=f"{env.affective_symbol} Price")
plt.legend()
plt.show()