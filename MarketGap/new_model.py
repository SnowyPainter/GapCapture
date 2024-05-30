import sys
sys.path.append('..')

import stockdata
import learn

print("코스피는 .KS, 코스닥은 .KQ를 붙여주세요.")
symbol1 = input("주식쌍 종목 코드(1/2) : ")
symbol2 = input("주식쌍 종목 코드(2/2) : ")

print("50일간의 데이터에서 5분 간격의 데이터를 뽑아 학습합니다.")

env = learn.MarketEnvironment(symbol1, symbol2, stockdata.today_before(50), stockdata.today(),"5m")

agent = learn.DQNAgent(env, 10000, 64)
agent.learn(50)
agent.save(f"./{symbol1[:6]}{symbol2[:6]}.keras")