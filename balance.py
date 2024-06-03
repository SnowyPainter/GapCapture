from KEYS import *
import mojito

broker = mojito.KoreaInvestment(api_key=REAL_KEY, api_secret=REAL_APISECRET, acc_no=REAL_ACCOUNT_NO, exchange='나스닥', mock=False)
resp = broker.fetch_present_balance()
print(resp)
stocks_qty = {}
avg_p = {}
for stock in resp['output1']:
    stocks_qty[stock['pdno']] = int(float(stock['ccld_qty_smtl1']))
    avg_p[stock['pdno']] = float(stock['avg_unpr3'])
print(stocks_qty)
print(avg_p)