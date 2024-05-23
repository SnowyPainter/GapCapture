import datetime
import mojito
import math
import time
import MarketGap.learn as learn, stockdata
import numpy as np
import pprint
import tensorflow as tf
import json
import pandas as pd

from KEYS import *
from settings import *
import log

def get_amount_of_sell(curr_units):
    n = curr_units
    if n > SELL_AMOUNT:
        n = SELL_AMOUNT
    return n
def get_amount_of_buy(curr_amount, stock_price):
    n = math.floor((curr_amount * (1-FEE)) / stock_price)
    if n > BUY_AMOUNT:
        n = BUY_AMOUNT
    return n

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
def set_entry_price(curr_entry_price, units, new_price):
    curr_entry_price += units * new_price
    curr_entry_price /= (1 if curr_entry_price == 0 else (units + 1))
    return curr_entry_price
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
    df['Datetime'] = [pd.to_datetime(stockdata.today(tz='Asia/Seoul'), format="%Y-%m-%d %H:%M:%S%z")]
    df.set_index('Datetime', inplace=True)
    return df
def reshape(state):
    return np.reshape(state, [1, 1, 2])

t = input("실전투자(y), 모의투자(n) : ")
k = REAL_KEY
s = REAL_APISECRET
a = REAL_ACCOUNT_NO
mock = False
SELL_AMOUNT = 4
BUY_AMOUNT = 4
subtitle = "실전투자"
if t != "y":
    SELL_AMOUNT = 30
    BUY_AMOUNT = 30
    k = KEY
    s = APISECRET
    a = ACCOUNT_NO
    mock = True
    subtitle = "모의투자"

logger = log.Logger(f"{SYMBOL1_NAME}, {SYMBOL2_NAME}", subtitle)
broker = mojito.KoreaInvestment(api_key=k, api_secret=s, acc_no=a, mock=mock)
agent = tf.keras.models.load_model("./MarketGap/hmsk.keras")
resp = broker.fetch_balance()
current_amount = int(resp['output2'][0]['prvs_rcdl_excc_amt'])
symbols = [SYMBOL1, SYMBOL2] #hanmi semiconductor / sk hynix
env = learn.MarketEnvironment(symbols[0]+".KS", symbols[1]+".KS", stockdata.today_before(14, tz='Asia/Seoul'), stockdata.today(tz='Asia/Seoul'),"5m")

stocks_qty = {}
for stock in resp['output1']:
    stocks_qty[stock['pdno']] = int(stock['hldg_qty'])

symbol1_units = 0 if not symbols[0] in stocks_qty else stocks_qty[symbols[0]]
symbol2_units = 0 if not symbols[1] in stocks_qty else stocks_qty[symbols[1]]

trades = 0
fee = FEE
net_wealths = list()

start_time = datetime.time(9, 0)
end_time = datetime.time(15, 30)

init_amount = current_amount

logger.log(f"평가 : {resp['output2'][0]['tot_evlu_amt']}")
logger.log(f"예수금 : {current_amount}")
logger.log(f"보유 종목 : {stocks_qty}")

symbol1_entry_price = 0
symbol2_entry_price = 0

def buy(logger, units, symbol, price, fee):
    global symbol1_entry_price, symbol2_entry_price, current_amount, trades
    buy_order(symbol, units)
    if symbol == symbols[0]:
        symbol1_entry_price = set_entry_price(symbol1_entry_price, units, price)
    elif symbol == symbols[1]:
        symbol2_entry_price = set_entry_price(symbol2_entry_price, units, price)
    current_amount -= units * price * (1+fee)
    logger.log(f"BUY {symbol} - {units} / {price}")
    trades += 1
    return units
def sell(logger, symbol, price, loss):
    global current_amount, trades
    if symbol == symbols[0]:
        units = get_amount_of_sell(symbol1_units)
    elif symbol == symbols[1]:
        units = get_amount_of_sell(symbol2_units)
    sell_order(symbol, units)
    current_amount += units * price
    logger.log(f"SOLD {symbol} - {units} / {price}, Profit : {loss}")
    trades += 1
    return units

while True:
    current_time = datetime.datetime.now().time()
    if True:#start_time <= current_time <= end_time:
        prices = create_prices(symbols[0], symbols[1])
        env.append_raw(prices)
        state = reshape(np.array([env.get_last()]))
        symbol1_price = prices.iloc[0][0]
        symbol2_price = prices.iloc[0][1]
        
        
        symbol1_loss = ((symbol1_price - symbol1_entry_price) / symbol1_entry_price) if symbol1_entry_price != 0 else 0
        symbol2_loss = ((symbol2_price - symbol2_entry_price) / symbol2_entry_price) if symbol2_entry_price != 0 else 0
        
        if symbol1_units > 0:
            if symbol1_loss >= TAKE_PROFIT or symbol1_loss <= STOP_LOSS:
                symbol1_units -= sell(logger, symbols[0], symbol1_price, symbol1_loss)
                
        if symbol2_units > 0:
            if symbol2_loss >= TAKE_PROFIT or symbol2_loss <= STOP_LOSS:
                symbol2_units -= sell(logger, symbols[1], symbol2_price, symbol2_loss)
            
        if symbol1_units <= 0:
            symbol1_entry_price = 0
        if symbol2_units <= 0:
            symbol2_entry_price = 0
        
        action = np.argmax(agent.predict(state, verbose=0)[0, 0])
        if action == 0:
            logger.log(f"{action} : Holding")
        else:
            if action == 1:
                if symbol2_units > 0:
                    symbol2_units -= sell(logger, symbols[1], symbol2_price, symbol2_loss)
                units = get_amount_of_buy(current_amount, symbol1_price)
                if units > 0:
                    symbol1_units += buy(logger, units, symbols[0], symbol1_price, fee)
                else:
                    logger.log(f"No Money to buy {symbols[0]} - {current_amount} / {symbol1_price}")
            elif action == 2:
                if symbol1_units > 0:
                    symbol1_units -= sell(logger, symbols[0], symbol1_price, symbol1_loss)
                units = get_amount_of_buy(init_amount, symbol2_price)
                if units > 0:
                    symbol2_units += buy(logger, units, symbols[1], symbol2_price, fee)
                else:
                    logger.log(f"No Money to buy {symbols[1]} - {current_amount} / {symbol2_price}")
        net_wealths.append(symbol1_units * symbol1_price + symbol2_units * symbol2_price + current_amount)
        time.sleep(60*5)
    else:
        time.sleep(60)
        
    if current_time >= end_time:
        logger.log(f"장 종료, Trades : {trades}")
        break