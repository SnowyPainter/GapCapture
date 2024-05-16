import MarketGap.learn as learn, stockdata

env = learn.MarketEnvironment("042700.KS", "000660.KS", stockdata.today_before(180), stockdata.today(),"1d")
print(env.corr())