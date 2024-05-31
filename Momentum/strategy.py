
BUY = 1
SELL = 2

class Strategy:
    def _normalize(self, df):
        mean, std = df.mean(), df.std()
        return (df - mean) / std
    def _calculate_profit(self, start, end):
        return (end - start) / start
        
    def __init__(self, price_df, term = 60) -> None:
        self.data = price_df
        self.norm_data = self._normalize(price_df)
        self.term = term
        self.bar = term
    def action(self):
        profit = self._calculate_profit(self.data.iloc[self.bar - self.term], self.data.iloc[self.bar])
        top_10_percent_threshold = profit.quantile(0.90)
        bottom_10_percent_threshold = profit.quantile(0.10)
        top_10_percent_stocks = profit[profit >= top_10_percent_threshold].index.tolist()
        bottom_10_percent_stocks = profit[profit <= bottom_10_percent_threshold].index.tolist()
        self.bar += 1
        return {
            BUY : top_10_percent_stocks,
            SELL : bottom_10_percent_stocks
        }, self.data.iloc[self.bar - 1]
        