from KEYS import *
import mojito

broker = mojito.KoreaInvestment(api_key=REAL_KEY, api_secret=REAL_APISECRET, acc_no=REAL_ACCOUNT_NO, mock=False)
resp = broker.fetch_balance()
stocks_qty = list()
for stock in resp['output1']:
    stocks_qty.append({stock['pdno'] : stock['hldg_qty'], "avgp" : stock['pchs_avg_pric']})

print(stocks_qty)