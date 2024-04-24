from KEYS import *
import mojito

broker = mojito.KoreaInvestment(api_key=KEY, api_secret=APISECRET, acc_no=ACCOUNT_NO, mock=True)
resp = broker.fetch_balance()
print(resp['output1'])
stocks_qty = list()
for stock in resp['output1']:
    stocks_qty.append({stock['pdno'] : stock['hldg_qty']})

print(stocks_qty)