import stockdata

df = stockdata.create_dataset(["042700.KS", "000660.KS"], "NVDA", stockdata.today_before(50), stockdata.today(), "5m")
