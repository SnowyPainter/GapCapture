import sys
sys.path.append('..')

import schedule
import time
import MarketGap.GapInvest as GapInvest
from KEYS import *

strategy1 = GapInvest.GapInvest(REAL_KEY, REAL_APISECRET, REAL_ACCOUNT_NO, False, "./hmsk.keras", "./hanmi_sk_settings.ini", "실전투자")

strategy1.run()

exit()

print("This program run investing algorithm every 09:00")
print("The log will be written at this directory.")

schedule.every().day.at("09:00").do(strategy1.run)

while True:
    schedule.run_pending()
    time.sleep(1)