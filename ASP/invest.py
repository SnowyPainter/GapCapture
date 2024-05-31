import sys
sys.path.append('..')
from datetime import datetime
import mojito
import math
import time
import learn, stockdata
import numpy as np
import pprint
import tensorflow as tf
import json
import pandas as pd
import log
import readini

class ASPInvest:
    def reshape(self, state):
        return np.reshape(state, [1, 1, 3])
    def get_amount_of_sell(self, curr_units):
        n = curr_units
        if n > self.config["SELL_AMOUNT"]:
            n = self.config["SELL_AMOUNT"]
        return n
    def get_amount_of_buy(self, curr_amount, stock_price):
        n = math.floor((curr_amount * (1-self.config["FEE"])) / (stock_price))
        if n > self.config["BUY_AMOUNT"]:
            n = self.config["BUY_AMOUNT"]
        return n
    def buy_order(self, symbol, qty, price): #market price
        resp = self.broker.create_market_buy_order(
            symbol=symbol,
            quantity=qty
        )
        if resp['msg1'] == "주문가능금액을 초과 했습니다":
            self.logger.log("시장가 매매 주문 가능 금액 부족으로 지정가 매수")
            resp = self.broker.create_limit_buy_order(
                symbol = symbol,
                price = price,
                quantity = qty,
            )
        pprint.pprint(resp)
        time.sleep(1)
    def sell_order(self, symbol, qty):
        resp = self.broker.create_market_sell_order(
            symbol=symbol,
            quantity=qty
        )
        pprint.pprint(resp)
        time.sleep(1)
    def buy(self, units, symbol, price):
        self.buy_order(symbol, units, price)
        self.current_amount -= units * price * (1+self.config["FEE"])
        self.logger.log(f"매수 주문 {symbol} - {units} / {price}")
        self.trades += 1
        return units
    def sell(self, symbol, price, loss):
        if symbol == self.config["CODE1"]:
            units = self.get_amount_of_sell(self.symbol1_units)
        elif symbol == self.config["CODE2"]:
            units = self.get_amount_of_sell(self.symbol2_units)
        self.sell_order(symbol, units)
        self.current_amount += units * price
        self.logger.log(f"시장가 매도 {symbol} - {units}, 예상 수익 : {loss}")
        self.trades += 1
        return units
    def create_logger(self, subtitle):
        self.logger = log.Logger(f"{self.config['NAME1']}, {self.config['NAME2']}", subtitle)
    def __init__(self, key, api_secret, account_no, mock, settings, subtitle=""):
        self.config = readini.read(settings)
        self.broker = mojito.KoreaInvestment(api_key=key, api_secret=api_secret, acc_no=account_no, mock=mock)
        self.agent = tf.keras.models.load_model(self.config['MODEL'])
        
        self.env = learn.ASPEnvironment(self.config["CODE1"]+f".{self.config['TAG1']}", self.config["CODE2"]+f".{self.config['TAG2']}", self.config['AFFECTIVE'], stockdata.today_before(14, tz='Asia/Seoul'), stockdata.today(tz='Asia/Seoul'),"5m")
        self.logger = None
        self.trades = 0
        self.subtitle = subtitle

    def run(self):
        resp = self.broker.fetch_balance()
        pprint.pprint(resp)
        stocks_qty = {}
        for stock in resp['output1']:
            stocks_qty[stock['pdno']] = int(stock['hldg_qty'])
        self.symbol1_units = 0 if not self.config["CODE1"] in stocks_qty else stocks_qty[self.config["CODE1"]]
        self.symbol2_units = 0 if not self.config["CODE2"] in stocks_qty else stocks_qty[self.config["CODE2"]]
        self.evaluate_amount = resp['output2'][0]['tot_evlu_amt']
        self.current_amount = int(resp['output2'][0]['prvs_rcdl_excc_amt'])
        self.create_logger(subtitle=self.subtitle)
        self.logger.log(f"평가 : {self.evaluate_amount}")
        self.logger.log(f"예수금 : {self.current_amount}")
        self.logger.log(f"보유 종목 : {self.config['NAME1']}({self.symbol1_units}), {self.config['NAME2']}({self.symbol2_units})")            
        while True:
            now = datetime.now()

            resp = self.broker.fetch_balance()
            avgp = {self.config["CODE1"]:0, self.config["CODE2"]:0}
            for stock in resp['output1']:
                avgp[stock['pdno']] = float(stock['pchs_avg_pric'])
            
            prices = self.env.new_prices()
            state = self.reshape(np.array([self.env.get_last()]))
            symbol1_price = prices.iloc[0][0]
            symbol2_price = prices.iloc[0][1]

            symbol1_loss = ((symbol1_price - avgp[self.config["CODE1"]]) / avgp[self.config["CODE1"]]) if avgp[self.config["CODE1"]] != 0 else 0
            symbol2_loss = ((symbol2_price - avgp[self.config["CODE2"]]) / avgp[self.config["CODE2"]]) if avgp[self.config["CODE2"]] != 0 else 0
            
            if self.symbol1_units > 0:
                if symbol1_loss >= self.config["TAKE_PROFIT"] or symbol1_loss <= self.config["STOP_LOSS"]:
                    self.symbol1_units -= self.sell(self.config["CODE1"], symbol1_price, symbol1_loss)
            if self.symbol2_units > 0:
                if symbol2_loss >= self.config["TAKE_PROFIT"] or symbol2_loss <= self.config["STOP_LOSS"]:
                    self.symbol2_units -= self.sell(self.config["CODE2"], symbol2_price, symbol2_loss)

            action = np.argmax(self.agent.predict(state, verbose=0)[0, 0])
            if action == 0:
                self.logger.log(f"Holding, {self.config['CODE1']}: {self.symbol1_units}, {self.config['CODE2']}: {self.symbol2_units}")
            else:
                if action == 1:
                    if self.symbol2_units > 0:
                        self.symbol2_units -= self.sell(self.config["CODE2"], symbol2_price, symbol2_loss)
                    units = self.get_amount_of_buy(self.current_amount, symbol1_price)
                    if units > 0:
                        self.symbol1_units += self.buy(units, self.config["CODE1"], symbol1_price)
                    else:
                        self.logger.log(f"No Money to buy {self.config['CODE1']} - {self.current_amount} / {symbol1_price}")
                elif action == 2:
                    if self.symbol1_units > 0:
                        self.symbol1_units -= self.sell(self.config["CODE1"], symbol1_price, symbol1_loss)
                    units = self.get_amount_of_buy(self.current_amount, symbol2_price)
                    if units > 0:
                        self.symbol2_units += self.buy(units, self.config["CODE2"], symbol2_price)
                    else:
                        self.logger.log(f"No Money to buy {self.config['CODE2']} - {self.current_amount} / {symbol2_price}")
            
            if now.hour >= 15 and now.minute >= 30:
                self.logger.log(f"End Trade, Trades:{self.trades}")
                break
            else:
                time.sleep(60*5)