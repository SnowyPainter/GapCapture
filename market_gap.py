import stockdata

df = stockdata.create_dataset(["nvda", "msft"], stockdata.today_before(100), stockdata.today(),"1d")
df = stockdata.normalize(df)

corr = df.corr()
print(corr)