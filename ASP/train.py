import sys
sys.path.append('..')

import stockdata
import learn
import readini

config = readini.read("./hanmi_sk_settings.ini")
symbol1 = config["CODE1"]+"."+config["TAG1"]
symbol2 = config["CODE2"]+"."+config["TAG2"]
affective = config["AFFECTIVE"]
env = learn.ASPEnvironment(symbol1, symbol2, affective, stockdata.today_before(50), stockdata.today(), "5m")

agent = learn.DQNAgent(env, 10000, 64)
agent.learn(50)
agent.save(f"./{symbol1[:6]}{symbol2[:6]}.keras")