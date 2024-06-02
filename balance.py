from KEYS import *
import mojito

broker = mojito.KoreaInvestment(api_key=REAL_KEY, api_secret=REAL_APISECRET, acc_no=REAL_ACCOUNT_NO, exchange='나스닥', mock=False)
resp = broker.fetch_present_balance()

print(resp['output2'])