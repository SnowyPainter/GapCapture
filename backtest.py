import stockdata
import tensorflow as tf
import numpy as np 
import math

def reshape(state):
    return np.reshape(state, [1, 1, 2])

class Strategy1:
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
        
        while bar < len(self.env.normalized_data) - 1:
            prices = self.get_price(bar)
            state = reshape(np.array([self.env.get_state(bar)]))
            action = np.argmax(self.agent.predict(state, verbose=0)[0, 0])
            # if 1
            # symbol 2 sell, symbol 1 buy
            # if 2
            # symbol 2 buy, symbol 1 sell
            # if 0 -> hold
            
            if action != 0:
                if action == 1:
                    if self.symbol2_units > 0:
                        self.symbol2_units -= self._sell(self.symbol2_units, prices[1])
                    symbol1_amount = math.floor(self.current_balance / prices[0])
                    if symbol1_amount > 0:
                        self.symbol1_units += self._buy(symbol1_amount, prices[0])
                elif action == 2:
                    if self.symbol1_units > 0:
                        self.symbol1_units -= self._sell(self.symbol1_units, prices[0])
                    symbol2_amount = math.floor(self.current_balance / prices[1])
                    if symbol2_amount > 0:
                        self.symbol2_units += self._buy(symbol2_amount, prices[1])
            
            self.net_wealths.append(self.symbol1_units * prices[0] + self.symbol2_units * prices[1] + self.current_balance)
            self.units = self.symbol1_units + self.symbol2_units
    
            bar += 1