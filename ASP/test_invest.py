import sys
sys.path.append('..')
# testing
import schedule
import time
import invest
from KEYS import *

strategy1 = invest.ASPInvest(REAL_KEY, REAL_APISECRET, REAL_ACCOUNT_NO, False, "./hanmi_sk_settings.ini", True, False,"실전투자")
strategy1.run()
while True:
    time.sleep(1)