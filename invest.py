import mojito
import math
import time
import learn, stockdata
import numpy as np
import pprint
import tensorflow as tf
import json
import datetime
import pandas as pd

from KEYS import *

#time.sleep(60*60 + 60*30)
#print("Start Trade")

def buy_order(symbol, qty): #market price
    resp = broker.create_market_buy_order(
        symbol=symbol,
        quantity=qty
    )
    pprint.pprint(resp)
    time.sleep(10)
def sell_order(symbol, qty):
    resp = broker.create_market_sell_order(
        symbol=symbol,
        quantity=qty
    )
    pprint.pprint(resp)
    time.sleep(10)

def get_price(symbol):
    resp = broker.fetch_price(symbol)
    return int(resp['output']['stck_prpr'])
def create_prices(symbol1, symbol2):
    df = pd.DataFrame()
    p1 = get_price(symbol1)
    time.sleep(1)
    p2 = get_price(symbol2)
    df[symbol1+'.KS_Price'] = [p1]
    df[symbol2+'.KS_Price'] = [p2]
    df['Datetime'] = [pd.to_datetime(stockdata.today(), format="%Y-%m-%d %H:%M:%S%z")]
    df.set_index('Datetime', inplace=True)
    return df
def reshape(state):
    return np.reshape(state, [1, 1, 2])

broker = mojito.KoreaInvestment(api_key=KEY, api_secret=APISECRET, acc_no=ACCOUNT_NO, mock=True)
agent = tf.keras.models.load_model("hmsk.keras")
resp = broker.fetch_balance()
current_amount = int(resp['output2'][0]['prvs_rcdl_excc_amt'])
symbols = ["042700", "000660"] #hanmi semiconductor / sk hynix
env = learn.MarketEnvironment(symbols[0]+".KS", symbols[1]+".KS", stockdata.today_before(50), stockdata.today(),"30m")

stocks_qty = {}
for stock in resp['output1']:
    stocks_qty[stock['pdno']] = int(stock['hldg_qty'])

symbol1_units = 0 if not symbols[0] in stocks_qty else stocks_qty[symbols[0]]
symbol2_units = 0 if not symbols[1] in stocks_qty else stocks_qty[symbols[1]]

print(f"평가 : {resp['output2'][0]['tot_evlu_amt']}")
print(f"예수금 : {current_amount}")
print(f"보유 종목 : {stocks_qty}")

trades = 0
fee = 0.005
net_wealths = list()

timeout = 60*60*6 #sec
timeout_start = time.time()
while time.time() < timeout_start + timeout:
    
    prices = create_prices(symbols[0], symbols[1])
    env.append_raw(prices)
    state = reshape(np.array([env.get_last()]))
    
    symbol1_price = prices.iloc[0][0]
    symbol2_price = prices.iloc[0][1]
    
    action = np.argmax(agent.predict(state, verbose=0)[0, 0])
    if action != 0:
        if action == 1:
            if symbol2_units > 0:
                sell_order(symbols[1], symbol2_units)
                current_amount += symbol2_units * symbol2_price
                symbol2_units -= symbol2_units
                trades += 1
            symbol1_amount = math.floor(current_amount / symbol1_price)
            if symbol1_amount > 0:
                if symbol2_units > 0:
                    sell_order(symbols[1], symbol2_units)
                    current_amount += symbol2_units * symbol2_price
                    symbol2_units -= symbol2_units
                buy_order(symbols[0], symbol1_amount)
                current_amount -= symbol1_amount * symbol1_price + symbol1_amount * fee
                symbol1_units += symbol1_amount
                trades += 1
        elif action == 2:
            if symbol1_units > 0:
                sell_order(symbols[0], symbol1_units)
                current_amount += symbol1_units * symbol1_price
                symbol1_units -= symbol1_units
                trades += 1
            symbol2_amount = math.floor(current_amount / symbol2_price)
            if symbol2_amount > 0:
                if symbol1_units > 0:
                    sell_order(symbols[0], symbol1_units)
                    current_amount += symbol1_units * symbol1_price
                    symbol1_units -= symbol1_units
                buy_order(symbols[1], symbol2_amount)
                current_amount -= symbol2_amount * symbol2_price + symbol2_amount * fee
                symbol2_units += symbol2_amount
                trades += 1
    net_wealths.append(symbol1_units * symbol1_price + symbol2_units * symbol2_price + current_amount)
    print(net_wealths[-1])
    
    time.sleep(60*5)
    
data = {
    "trades" : trades,
    "net wealths" : net_wealths
}

with open(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}.json', 'w') as f:
    json.dump(data, f)