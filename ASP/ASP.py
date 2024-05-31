import sys
sys.path.append('..')

import stockdata
import readini
import learn, backtest
import matplotlib.pyplot as plt

settings = "./hanmi_sk_settings.ini"
config = readini.read(settings)
symbol1 = str(config["CODE1"]) + "." + config["TAG1"]
symbol2 = str(config["CODE1"]) + "." + config["TAG2"]
print(symbol1, symbol2)
env = learn.ASPEnvironment(symbol1, symbol2, config["AFFECTIVE"], stockdata.today_before(50), stockdata.today(),"5m")

amount = 100000000
stgy = backtest.Strategy1(env, amount, 0.0025, config["MODEL"])
stgy.run()
print((stgy.net_wealths[-1] - amount) / amount)
plt.plot(stgy.net_wealths)
plt.show()