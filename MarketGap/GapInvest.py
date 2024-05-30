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
import configparser

class GapInvest:
    def reshape(self, state):
        return np.reshape(state, [1, 1, 2])
    def get_amount_of_sell(self, curr_units):
        n = curr_units
        if n > self.SELL_AMOUNT:
            n = self.SELL_AMOUNT
        return n
    def get_amount_of_buy(self, curr_amount, stock_price):
        n = math.floor((curr_amount * (1-self.FEE)) / (stock_price))
        if n > self.BUY_AMOUNT:
            n = self.BUY_AMOUNT
        return n
    def buy_order(self, symbol, qty, price): #market price
        print(qty)
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
    def get_price(self, symbol):
        resp = self.broker.fetch_price(symbol)
        return int(resp['output']['stck_prpr'])
    def create_prices(self, symbol1, symbol2):
        df = pd.DataFrame()
        p1 = self.get_price(symbol1)
        time.sleep(1)
        p2 = self.get_price(symbol2)
        df[symbol1+ f'.{self.TAG1}_Price'] = [p1]
        df[symbol2+ f'.{self.TAG2}_Price'] = [p2]
        df['Datetime'] = [pd.to_datetime(stockdata.today(tz='Asia/Seoul'), format="%Y-%m-%d %H:%M:%S%z")]
        df.set_index('Datetime', inplace=True)
        return df
    def buy(self, units, symbol, price):
        self.buy_order(symbol, units, price)
        self.current_amount -= units * price * (1+self.FEE)
        self.logger.log(f"매수 주문 {symbol} - {units} / {price}")
        self.trades += 1
        return units
    def sell(self, symbol, price, loss):
        if symbol == self.SYMBOL1:
            units = self.get_amount_of_sell(self.symbol1_units)
        elif symbol == self.SYMBOL2:
            units = self.get_amount_of_sell(self.symbol2_units)
        self.sell_order(symbol, units)
        self.current_amount += units * price
        self.logger.log(f"시장가 매도 {symbol} - {units}, 예상 수익 : {loss}")
        self.trades += 1
        return units
    def create_logger(self, subtitle):
        self.logger = log.Logger(f"{self.SYMBOL1_NAME}, {self.SYMBOL2_NAME}", subtitle)
    def __init__(self, key, api_secret, account_no, mock, settings, subtitle=""):
        config = configparser.ConfigParser()
        config.read(settings)
        self.TAG1 = config['SETTINGS']['SYMBOL1_TAG']
        self.TAG2 = config['SETTINGS']['SYMBOL2_TAG']
        self.SELL_AMOUNT = config['SETTINGS'].getint('SELL_AMOUNT')
        self.BUY_AMOUNT = config['SETTINGS'].getint('BUY_AMOUNT')
        self.SYMBOL1 = config['SETTINGS']['SYMBOL1']
        self.SYMBOL1_NAME = config['SETTINGS']['SYMBOL1_NAME']
        self.SYMBOL2 = config['SETTINGS']['SYMBOL2']
        self.SYMBOL2_NAME = config['SETTINGS']['SYMBOL2_NAME']
        self.FEE = config['SETTINGS'].getfloat('FEE')
        self.TAKE_PROFIT = config['SETTINGS'].getfloat('TAKE_PROFIT')
        self.STOP_LOSS = config['SETTINGS'].getfloat('STOP_LOSS')
        
        self.broker = mojito.KoreaInvestment(api_key=key, api_secret=api_secret, acc_no=account_no, mock=mock)
        self.agent = tf.keras.models.load_model(config['MODEL']['PATH'])
        
        self.env = learn.MarketEnvironment(self.SYMBOL1+f".{self.TAG1}", self.SYMBOL2+f".{self.TAG1}", stockdata.today_before(14, tz='Asia/Seoul'), stockdata.today(tz='Asia/Seoul'),"5m")
        self.logger = None
        self.trades = 0
        self.subtitle = subtitle

    def run(self):
        resp = self.broker.fetch_balance()
        pprint.pprint(resp)
        stocks_qty = {}
        for stock in resp['output1']:
            stocks_qty[stock['pdno']] = int(stock['hldg_qty'])
        self.symbol1_units = 0 if not self.SYMBOL1 in stocks_qty else stocks_qty[self.SYMBOL1]
        self.symbol2_units = 0 if not self.SYMBOL2 in stocks_qty else stocks_qty[self.SYMBOL2]
        self.evaluate_amount = resp['output2'][0]['tot_evlu_amt']
        self.current_amount = int(resp['output2'][0]['prvs_rcdl_excc_amt'])
        self.create_logger(subtitle=self.subtitle)
        print(f"{self.SYMBOL1_NAME}, {self.SYMBOL2_NAME} Gap Investment Machine Started")
        self.logger.log(f"평가 : {self.evaluate_amount}")
        self.logger.log(f"예수금 : {self.current_amount}")
        self.logger.log(f"보유 종목 : {self.SYMBOL1_NAME}({self.symbol1_units}), {self.SYMBOL2_NAME}({self.symbol2_units})")            
        while True:
            now = datetime.now()

            resp = self.broker.fetch_balance()
            avgp = {self.SYMBOL1:0, self.SYMBOL2:0}
            for stock in resp['output1']:
                avgp[stock['pdno']] = float(stock['pchs_avg_pric'])

            prices = self.create_prices(self.SYMBOL1, self.SYMBOL2)
            self.env.append_raw(prices)
            state = self.reshape(np.array([self.env.get_last()]))
            symbol1_price = prices.iloc[0][0]
            symbol2_price = prices.iloc[0][1]

            symbol1_loss = ((symbol1_price - avgp[self.SYMBOL1]) / avgp[self.SYMBOL1]) if avgp[self.SYMBOL1] != 0 else 0
            symbol2_loss = ((symbol2_price - avgp[self.SYMBOL2]) / avgp[self.SYMBOL2]) if avgp[self.SYMBOL2] != 0 else 0
            
            if self.symbol1_units > 0:
                if symbol1_loss >= self.TAKE_PROFIT or symbol1_loss <= self.STOP_LOSS:
                    self.symbol1_units -= self.sell(self.SYMBOL1, symbol1_price, symbol1_loss)
            if self.symbol2_units > 0:
                if symbol2_loss >= self.TAKE_PROFIT or symbol2_loss <= self.STOP_LOSS:
                    self.symbol2_units -= self.sell(self.SYMBOL2, symbol2_price, symbol2_loss)

            action = np.argmax(self.agent.predict(state, verbose=0)[0, 0])
            if action == 0:
                self.logger.log(f"Holding, {self.SYMBOL1}: {self.symbol1_units}, {self.SYMBOL2}: {self.symbol2_units}")
            else:
                if action == 1:
                    if self.symbol2_units > 0:
                        self.symbol2_units -= self.sell(self.SYMBOL2, symbol2_price, symbol2_loss)
                    units = self.get_amount_of_buy(self.current_amount, symbol1_price)
                    if units > 0:
                        self.symbol1_units += self.buy(units, self.SYMBOL1, symbol1_price)
                    else:
                        self.logger.log(f"No Money to buy {self.SYMBOL1} - {self.current_amount} / {symbol1_price}")
                elif action == 2:
                    if self.symbol1_units > 0:
                        self.symbol1_units -= self.sell(self.SYMBOL1, symbol1_price, symbol1_loss)
                    units = self.get_amount_of_buy(self.current_amount, symbol2_price)
                    if units > 0:
                        self.symbol2_units += self.buy(units, self.SYMBOL2, symbol2_price)
                    else:
                        self.logger.log(f"No Money to buy {self.SYMBOL2} - {self.current_amount} / {symbol2_price}")
            
            if now.hour >= 15 and now.minute >= 30:
                self.logger.log(f"End Trade, Trades:{self.trades}")
                break
            else:
                time.sleep(60*5)