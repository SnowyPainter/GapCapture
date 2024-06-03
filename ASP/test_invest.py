import sys
sys.path.append('..')
# testing
import schedule
import time
import invest
from KEYS import *

strategy1 = invest.ASPInvest(REAL_KEY, REAL_APISECRET, REAL_ACCOUNT_NO, False, "./moln_holo_settings.ini", True, True,"실전투자")
strategy1.run()
while True:
    time.sleep(1)