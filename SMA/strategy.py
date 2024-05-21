import pandas as pd
import numpy

HOLD = 0
BUY = 1
SELL = 2

class Strategy:
    def _normalize(self):
        mean, std = self.prices.mean(), self.prices.std()
        self.norm_prices = (self.prices - mean) / std
    def append_price(self, prices):
        self.prices = pd.concat([self.prices, prices])
        self._normalize()
    def __init__(self, past_price, sma_window, lma_window):
        self.prices = past_price
        self.sma_window = sma_window
        self.lma_window = lma_window
        self._normalize()
        
    def action(self):
        #sma , lma
        sma = self.norm_prices.rolling(window=self.sma_window).mean()
        lma = self.norm_prices.rolling(window=self.lma_window).mean()
        sma_tail = sma.iloc[-1][0]
        lma_tail = lma.iloc[-1][0]
        sma_shifted = sma.shift(1).iloc[-1][0]
        if sma_tail > lma_tail and sma_tail >= sma_shifted:
            return BUY
        elif sma_tail < lma_tail and sma_tail < sma_shifted:
            return SELL
        else:
            return HOLD