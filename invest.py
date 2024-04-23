import mojito
import math
import time
import threading
import numpy as np
import pprint
import tensorflow as tf
import json
import datetime

from KEYS import *


def buy_order(symbol, qty): #market price
    resp = broker.create_market_buy_order(
        symbol=symbol,
        quantity=qty
    )
    pprint.pprint(resp)
    time.sleep(1)
def sell_order(symbol, qty):
    resp = broker.create_market_sell_order(
        symbol=symbol,
        quantity=qty
    )
    pprint.pprint(resp)
    time.sleep(1)

def get_price(symbol):
    resp = broker.fetch_price(symbol)
    return resp['output']['stck_prpr']
def create_prices(symbol1, symbol2):
    p1 = get_price(symbol1)
    time.sleep(1)
    p2 = get_price(symbol2)
    return np.array([int(p1), int(p2)])
def reshape(state):
    return np.reshape(state, [1, 1, 2])

broker = mojito.KoreaInvestment(api_key=KEY, api_secret=APISECRET, acc_no=ACCOUNT_NO, mock=True)
agent = tf.keras.models.load_model("nvdask.keras")
resp = broker.fetch_balance()
current_amount = int(resp['output2'][0]['dnca_tot_amt'])
symbols = ["042700", "000660"] #hanmi semiconductor / sk hynix

symbol1_balance = int(current_amount / 2)
symbol2_balance = int(current_amount / 2)
symbol1_units = 0
symbol2_units = 0
trades = 0
fee = 0.005
net_wealths = list()

timeout = 60*60*6 #sec
timeout_start = time.time()
while time.time() < timeout_start + timeout:
    
    prices = create_prices(symbols[0], symbols[1])
    state = reshape(np.array([prices]))
    action = np.argmax(agent.predict(state, verbose=0)[0, 0])
    if action != 0:
        if action == 1:
            if symbol2_units > 0:
                sell_order(symbols[1], symbol2_units)
                symbol2_balance += symbol2_units * prices[1]
                symbol2_units -= symbol2_units
                trades += 1
            symbol1_amount = math.floor(symbol1_balance / prices[0])
            if symbol1_amount > 0:
                buy_order(symbols[0], symbol1_amount)
                symbol1_balance -= symbol1_amount * prices[0] + symbol1_amount * fee
                symbol1_units += symbol1_amount
                trades += 1
        elif action == 2:
            if symbol1_units > 0:
                sell_order(symbols[0], symbol1_units)
                symbol1_balance += symbol1_units * prices[0]
                symbol1_units -= symbol1_units
                trades += 1
            symbol2_amount = math.floor(symbol2_balance / prices[1])
            if symbol2_amount > 0:
                buy_order(symbols[1], symbol2_amount)
                symbol2_balance -= symbol2_amount * prices[1] + symbol2_amount * fee
                symbol2_units += symbol2_amount
                trades += 1
            
    net_wealths.append(symbol1_units * prices[0] + symbol2_units * prices[1] + symbol1_balance + symbol2_balance)
    
    time.sleep(60*5)
    
data = {
    "trades" : trades,
    "net wealths" : net_wealths
}

with open(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}.json', 'w') as f:
    json.dump(data, f)