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
import pytz, os

class ASPInvest:
    def _create_standard_df(self, prices):
        df = pd.DataFrame()
        i = 0
        for symbol in self.yfsymbols:
            df[symbol+"_Price"] = [prices[i]]
            i += 1
        df['Datetime'] = [pd.to_datetime(stockdata.today(tz='Asia/Seoul'), format="%Y-%m-%d %H:%M:%S%z")]
        df.set_index('Datetime', inplace=True)
        return df
    def _create_now_data(self, symbols, affective, is_symbols_nyse ,is_affective_nyse):
        prices = []
        affective = affective.upper()
        if is_symbols_nyse and is_affective_nyse:
            symbols.append(affective)
            for symbol in symbols:
                resp = self.nyse_broker.fetch_price(symbol)
                prices.append(float(resp['output']['last']))
        elif not is_symbols_nyse and is_affective_nyse:
            for symbol in symbols:
                resp = self.broker.fetch_price(symbol)
                prices.append(float(resp['output']['stck_prpr']))    
            resp = self.nyse_broker.fetch_price(affective)
            prices.append(float(resp['output']['last']))
        elif is_symbols_nyse and not is_affective_nyse:
            for symbol in symbols:
                resp = self.nyse_broker.fetch_price(symbol)
                prices.append(float(resp['output']['last']))
            resp = self.broker.fetch_price(affective)
            prices.append(float(resp['output']['stck_prpr']))
        return prices
    
    def reshape(self, state):
        return np.reshape(state, [1, 1, 3])
    def is_market_closed(self, now):
        if self.is_symbol_nyse:
            return now.hour >= 16
        else:
            return now.hour >= 15 and now.minute >= 30
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
    def get_balance(self):
        if self.is_symbol_nyse:
            broker = self.nyse_broker
            resp = broker.fetch_present_balance()
            amount = 0 #resp['output2']['frcr_dncl_amt_2']
            stocks_qty = {}
            avgp = {self.config["CODE1"]:0, self.config["CODE2"]:0}
            for stock in resp['output1']:
                stocks_qty[stock['pdno']] = int(float(stock['ccld_qty_smtl1']))
                avgp[stock['pdno']] = float(stock['avg_unpr3'])
        else:
            broker = self.broker
            resp = broker.fetch_balance()
            amount = int(resp['output2'][0]['prvs_rcdl_excc_amt'])
            stocks_qty = {}
            avgp = {self.config["CODE1"]:0, self.config["CODE2"]:0}
            for stock in resp['output1']:
                stocks_qty[stock['pdno']] = int(stock['hldg_qty'])
                avgp[stock['pdno']] = float(stock['pchs_avg_pric'])
        return amount, stocks_qty, avgp

    def buy_order(self, symbol, qty, price): #market price
        broker = self.broker
        if self.is_symbol_nyse:
            broker = self.nyse_broker
        else:
            price = str(int(price))
            qty = str(qty)
        
        resp = broker.create_limit_buy_order(
            symbol = symbol,
            price = price,
            quantity = qty,
        )
        
        pprint.pprint(resp)
        time.sleep(1)

    def sell_order(self, symbol, qty, price):
        broker = self.broker
        if self.is_symbol_nyse:
            broker = self.nyse_broker
        else:
            price = str(int(price))
            qty = str(qty)
        
        resp = broker.create_limit_sell_order(
            symbol=symbol,
            price=price,
            quantity=qty
        )
        pprint.pprint(resp)
        time.sleep(1)

    def buy(self, units, symbol, price, af_price):
        self.buy_order(symbol, units, price)
        self.affective_entry_price += af_price
        self.affective_entry_price /= 2
        self.current_amount -= units * price * (1+self.config["FEE"])
        self.logger.log(f"매수 주문 {symbol} - {units} / {price}")
        self.trades += 1
        return units

    def sell(self, symbol, price, loss):
        if symbol == self.config["CODE1"]:
            units = self.get_amount_of_sell(self.symbol1_units)
        elif symbol == self.config["CODE2"]:
            units = self.get_amount_of_sell(self.symbol2_units)
        self.sell_order(symbol, units, price)
        self.current_amount += units * price
        self.logger.log(f"시장가 매도 {symbol} - {units}, 예상 수익 : {loss}")
        self.trades += 1
        return units
    def batch_sell(self, symbol1_price, symbol2_price, symbol1_loss, symbol2_loss):
        if self.symbol1_units > 0:
            self.symbol1_units -= self.sell(self.config["CODE1"], symbol1_price, symbol1_loss)
        if self.symbol2_units > 0:
            self.symbol2_units -= self.sell(self.config["CODE2"], symbol2_price, symbol2_loss)
    def batch_buy(self, symbol1_price, symbol2_price, af_price):
        units = self.get_amount_of_buy(self.current_amount, symbol1_price)
        if units > 0:
            self.symbol1_units += self.buy(units, self.config["CODE1"], symbol1_price, af_price)
        else:
            self.logger.log(f"[AFFECTIVE BUY] Lack of Money {self.config['CODE1']} - {self.current_amount} / {symbol1_price}")
        units = self.get_amount_of_buy(self.current_amount, symbol2_price)
        if units > 0:
            self.symbol2_units += self.buy(units, self.config["CODE2"], symbol2_price, af_price)
        else:
            self.logger.log(f"[AFFECTIVE BUY] Lack of Money {self.config['CODE2']} - {self.current_amount} / {symbol2_price}")
        
    def create_logger(self, subtitle):
        self.logger = log.Logger(f"{self.config['NAME1']}, {self.config['NAME2']}", subtitle)
    
    def __init__(self, key, api_secret, account_no, mock, settings, is_affective_nyse, is_symbol_nyse,  subtitle=""):
        self.config = readini.read(settings)
        self.broker = mojito.KoreaInvestment(api_key=key, api_secret=api_secret, acc_no=account_no, mock=mock)
        self.nyse_broker = mojito.KoreaInvestment(api_key=key, api_secret=api_secret, acc_no=account_no, exchange='나스닥', mock=mock)
        self.agent = tf.keras.models.load_model(self.config['MODEL'])
        self.is_affective_nyse = is_affective_nyse
        self.is_symbol_nyse = is_symbol_nyse
        if is_symbol_nyse:
            self.yfsymbols = [self.config["CODE1"], self.config["CODE2"], self.config['AFFECTIVE']]
        else:
            self.yfsymbols = [self.config["CODE1"]+f".{self.config['TAG1']}", self.config["CODE2"]+f".{self.config['TAG2']}", self.config['AFFECTIVE']]

        self.env = learn.ASPEnvironment(self.yfsymbols[0], self.yfsymbols[1], self.yfsymbols[2], stockdata.today_before(14, tz='Asia/Seoul'), stockdata.today(tz='Asia/Seoul'),"5m")
        self.logger = None
        self.trades = 0
        self.subtitle = subtitle

    def run(self):
        
        amount, stocks_qty, stocks_avgp = self.get_balance()
        prices = self._create_now_data([self.config["CODE1"], self.config["CODE2"]], self.config["AFFECTIVE"], self.is_symbol_nyse ,self.is_affective_nyse)
        self.affective_entry_price = prices[2]
        self.symbol1_units = 0 if not self.config["CODE1"] in stocks_qty else stocks_qty[self.config["CODE1"]]
        self.symbol2_units = 0 if not self.config["CODE2"] in stocks_qty else stocks_qty[self.config["CODE2"]]
        self.current_amount = amount
        
        if not os.path.exists('invest log'):
            os.makedirs('invest log')
        self.create_logger(subtitle=self.subtitle)
        self.logger.log(f"예수금 : {self.current_amount}")
        self.logger.log(f"보유 종목 : {self.config['NAME1']}({self.symbol1_units}), {self.config['NAME2']}({self.symbol2_units})")            
        self.logger.log(f"Affective System running {self.config['AFFECTIVE']} : {self.affective_entry_price}")
        if self.is_symbol_nyse:
            tz = pytz.timezone('America/New_York')
        else:
            tz = pytz.timezone('Asia/Seoul')
        while True:
            now = datetime.now(tz)
            amount, stocks_qty, stocks_avgp = self.get_balance()
            
            prices = self._create_now_data([self.config["CODE1"], self.config["CODE2"]], self.config["AFFECTIVE"], self.is_symbol_nyse, self.is_affective_nyse)
            self.env.append_raw(self._create_standard_df(prices))
            state = self.reshape(np.array([self.env.get_last()]))
            symbol1_price = prices[0]
            symbol2_price = prices[1]

            symbol1_loss = ((symbol1_price - stocks_avgp[self.config["CODE1"]]) / stocks_avgp[self.config["CODE1"]]) if stocks_avgp[self.config["CODE1"]] != 0 else 0
            symbol2_loss = ((symbol2_price - stocks_avgp[self.config["CODE2"]]) / stocks_avgp[self.config["CODE2"]]) if stocks_avgp[self.config["CODE2"]] != 0 else 0
            affective_loss = ((prices[2] - self.affective_entry_price) / self.affective_entry_price) if self.affective_entry_price != 0 else 0

            #Affective System
            if affective_loss > self.config["AF_BUY_THRESHOLD"]:
                self.batch_buy(symbol1_price, symbol2_price, prices[2])
            #elif affective_loss < self.config["AF_SELL_THRESHOLD"]:
            #    self.batch_sell(symbol1_price, symbol2_price, symbol1_loss, symbol2_loss, prices[2])
            
            if self.symbol1_units > 0:
                if symbol1_loss >= self.config["TAKE_PROFIT"]: #or symbol1_loss <= self.config["STOP_LOSS"]:
                    self.symbol1_units -= self.sell(self.config["CODE1"], symbol1_price, symbol1_loss)
            if self.symbol2_units > 0:
                if symbol2_loss >= self.config["TAKE_PROFIT"]: #or symbol2_loss <= self.config["STOP_LOSS"]:
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
                        self.symbol1_units += self.buy(units, self.config["CODE1"], symbol1_price, prices[2])
                    else:
                        self.logger.log(f"No Money to buy {self.config['CODE1']} - {self.current_amount} / {symbol1_price}")
                elif action == 2:
                    if self.symbol1_units > 0:
                        self.symbol1_units -= self.sell(self.config["CODE1"], symbol1_price, symbol1_loss)
                    units = self.get_amount_of_buy(self.current_amount, symbol2_price)
                    if units > 0:
                        self.symbol2_units += self.buy(units, self.config["CODE2"], symbol2_price, prices[2])
                    else:
                        self.logger.log(f"No Money to buy {self.config['CODE2']} - {self.current_amount} / {symbol2_price}")
            
            if self.is_market_closed(now):
                self.logger.log(f"End Trade, Trades:{self.trades}")
                break
            else:
                time.sleep(60*5)