import stockdata
import tensorflow as tf
import numpy as np 
import math

def reshape(state):
    return np.reshape(state, [1, 1, 2])

class Strategy1:
    def _affordable_stocks(self, stock_price, percent, affordables):
        n = math.floor((self.amount * percent) / stock_price)
        if n >= affordables:
            n = affordables
        return n

    def _sell(self, units, price):
        self.current_balance += units * price - units * self.fee
        self.trades += 1
        return units
    def _buy(self, units, price):
        self.current_balance -= units * price + units * self.fee
        self.trades += 1
        return units
    
    def __init__(self, env, amount, fee):
        self.agent = tf.keras.models.load_model("hmsk.keras")
        self.env = env
        self.amount = amount
        self.fee = fee
    
    def get_price(self, bar):
        prices = self.env.raw.iloc[bar]
        prices = np.array(prices)
        prices[1] /= 1250 # currency ratio
        return prices
    
    def test(self):
        self.units = 0
        self.position = 0
        self.trades = 0

        self.entry_price = 0
        
        self.net_wealths = list()
        bar = 1
        self.current_balance = self.amount
        self.symbol1_units = 0
        self.symbol2_units = 0
        
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
            if action == 0:
                print("홀딩")
            if action != 0:
                if action == 1:
                    if self.symbol2_units > 0:
                        units = self._affordable_stocks(prices[1], deal_percent, self.symbol2_units)
                        print(f"symbol2 {units} 매도")
                        self.symbol2_units -= self._sell(units, prices[1])
                    symbol1_amount = math.floor((self.current_balance) / prices[0])
                    units = self._affordable_stocks(prices[0], deal_percent, symbol1_amount)
                    if units > 0:
                        print(f"symbol1 {units} 매수")
                        self.symbol1_units += self._buy(units, prices[0])
                elif action == 2:
                    if self.symbol1_units > 0:
                        units = self._affordable_stocks(prices[0], deal_percent, self.symbol1_units)
                        print(f"symbol1 {units} 매도")
                        self.symbol1_units -= self._sell(units, prices[0])
                    symbol2_amount = math.floor((self.current_balance) / prices[1])
                    units = self._affordable_stocks(prices[1], deal_percent, symbol2_amount)
                    if units > 0:
                        print(f"symbol2 {units} 매수")
                        self.symbol2_units += self._buy(units, prices[1])
            
            nw = self.symbol1_units * prices[0] + self.symbol2_units * prices[1] + self.current_balance
            #print(nw)
            self.net_wealths.append(nw)
            self.units = self.symbol1_units + self.symbol2_units
    
            bar += 1