import stockdata

class GapFinder:
    def _normalize(self):
        mean, std = self.raw.mean(), self.raw.std()
        self.normalized_data = (self.raw - mean) / std
    
    def __init__(self, symbol1, symbol2, start, end, interval):
        self.symbols = [symbol1, symbol2]
        self.raw = stockdata.create_dataset(self.symbols, start, end, interval)
        self._normalize()
    
    def append_raw(self, df):
        self.raw.append(df)
        self._normalize()
        
    def get_buy_list(self, threshold):
        symbol1_price = self.normalized_data[self.symbols[0]+"_Price"]
        symbol2_price = self.normalized_data[self.symbols[1]+"_Price"]
        diff = symbol1_price - symbol2_price
        diff = diff.loc[abs(diff) >= threshold]
        return diff.map(lambda x: 1 if x < 0 else 1)
        
    def corr(self):
        return self.normalized_data.corr()

tickers = ["nvda", "000660.KS"]
stream = GapFinder("nvda", "000660.KS", stockdata.today_before(100), stockdata.today(),"1d")
stream.append_raw(stockdata.create_realtime_dataset(tickers))

print(stream.get_buy_list(0.3))