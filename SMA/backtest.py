import sys
sys.path.append('..')

import strategy
import math

class BacktestUnit:
    def _max_units(self, price):
        return math.floor(self.current_amount / price)

    def _buy(self, price, units):
        return units * price * 1.0025

    def _sell(self, price, units):
        return units * price * 0.9975
    
    def __init__(self, stgy, init_amount) -> None:
        self.init_amount = init_amount
        self.strategy = stgy
    
    def test(self):
        net_wealth = list()
        units = 0
        self.current_amount = self.init_amount
        self.bar = self.strategy.lma_window
        while self.bar < len(self.strategy.prices):
            action = self.strategy.action()
            price = self.strategy.prices.iloc[self.bar][0]
            if action == strategy.BUY:
                units += self._max_units(price)
                self.current_amount -= self._buy(price, units)
            elif action == strategy.SELL:
                self.current_amount += self._sell(price, units)
                units = 0

            net_wealth.append(self.current_amount + units * price)
            
            self.bar += 1
            
        return net_wealth