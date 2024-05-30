import stockdata
import tensorflow as tf
import numpy as np 
import math

def reshape(state):
    return np.reshape(state, [1, 1, 2])

class Strategy1:
    def get_amount_of_sell(self, curr_units):
        n = curr_units
        if n > 120:
            n = 120
        return n
    def get_amount_of_buy(self, stock_price):
        n = math.floor(self.current_balance / stock_price)
        if n > 120:
            n = 120
        return n
    
    def set_entry_price_symbol1(self, units, new_prices):
        self.entry_price_symbol1 += units * new_prices
        self.entry_price_symbol1 /= (1 if self.entry_price_symbol1 == 0 else (units + 1))
    def set_entry_price_symbol2(self, units, new_prices):
        self.entry_price_symbol2 += units * new_prices
        self.entry_price_symbol2 /= (1 if self.entry_price_symbol2 == 0 else (units + 1))

    def _sell(self, units, price):
        self.current_balance += units * price - units * self.fee
        self.trades += 1
        return units
    def _buy(self, units, price):
        self.current_balance -= units * price + units * self.fee
        self.trades += 1
        return units
    
    def __init__(self, env, amount, fee, model):
        self.agent = tf.keras.models.load_model(model)
        self.env = env
        self.amount = amount
        self.fee = fee
    
    def get_price(self, bar):
        prices = self.env.raw.iloc[bar]
        prices = np.array(prices)
        #prices[1] /= 1250 # currency ratio
        return prices
    
    def test(self):
        self.units = 0
        self.position = 0
        self.trades = 0
        self.net_wealths = list()
        bar = 1
        self.current_balance = self.amount
        self.symbol1_units = 0
        self.symbol2_units = 0
        
        self.entry_price_symbol1 = 0
        self.entry_price_symbol2 = 0
        
        deal_percent = 0.2

        while bar < len(self.env.normalized_data) - 1:
            prices = self.get_price(bar)
            state = reshape(np.array([self.env.get_state(bar)]))
            action = np.argmax(self.agent.predict(state, verbose=0)[0, 0])
            # if 1
            # symbol 2 sell, symbol 1 buy
            # if 2
            # symbol 2 buy, symbol 1 sell
            # if 0 -> hold
            
            symbol1_loss = ((prices[0] - self.entry_price_symbol1) / self.entry_price_symbol1) if self.entry_price_symbol1 != 0 else 0
            symbol2_loss = ((prices[1] - self.entry_price_symbol2) / self.entry_price_symbol2) if self.entry_price_symbol2 != 0 else 0
            
            
            if self.symbol1_units > 0:
                units = self.get_amount_of_sell(self.symbol1_units)
                if symbol1_loss > 0.035: #tp
                    print(f"이익 초과 symbol1 {units} / {symbol1_loss} 매도")
                    self.symbol1_units -= self._sell(units, prices[0])
                elif symbol1_loss < -0.045:
                    print(f"손절 symbol1 {units} / {symbol1_loss} 매도")
                    self.symbol1_units -= self._sell(units, prices[0])
            if self.symbol2_units > 0:
                units = self.get_amount_of_sell(self.symbol2_units)
                if symbol2_loss > 0.035:
                    print(f"이익 초과 symbol2 {units} / {symbol2_loss} 매도")
                    self.symbol2_units -= self._sell(units, prices[1])
                elif symbol2_loss < -0.045:
                    print(f"손절 symbol2 {units} / {symbol2_loss} 매도")
                    self.symbol2_units -= self._sell(units, prices[1])
            
            
            if action == 0:
                print(f"홀딩 {self.current_balance}")
            if action != 0:
                if action == 1:
                    if self.symbol2_units > 0:
                        units = self.get_amount_of_sell(self.symbol2_units)
                        print(f"symbol2 {units} 매도 {self.current_balance}")
                        self.symbol2_units -= self._sell(units, prices[1])
                        if self.symbol2_units <= 0:
                            self.entry_price_symbol2 = 0
                    units = self.get_amount_of_buy(prices[0])
                    if units > 0:
                        self.set_entry_price_symbol1(units, prices[0])
                        print(f"symbol1 {units} 매수 {self.current_balance} 평단 : {self.entry_price_symbol1}")
                        self.symbol1_units += self._buy(units, prices[0])
                elif action == 2:
                    if self.symbol1_units > 0:
                        units = self.get_amount_of_sell(self.symbol1_units)
                        print(f"symbol1 {units} 매도 {self.current_balance}")
                        self.symbol1_units -= self._sell(units, prices[0])
                        if self.symbol1_units <= 0:
                            self.entry_price_symbol1 = 0
                    units = self.get_amount_of_buy(prices[1])
                    if units > 0:
                        self.set_entry_price_symbol2(units, prices[1])
                        print(f"symbol2 {units} 매수 {self.current_balance} 평단 : {self.entry_price_symbol2}")
                        self.symbol2_units += self._buy(units, prices[1])
            
            nw = self.symbol1_units * prices[0] + self.symbol2_units * prices[1] + self.current_balance
            #print(nw)
            self.net_wealths.append(nw)
            self.units = self.symbol1_units + self.symbol2_units
    
            bar += 1