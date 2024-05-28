import sys
sys.path.append('..')

import schedule
import time
import invest
from KEYS import *

strategy1 = invest.GapInvest(KEY, APISECRET, ACCOUNT_NO, True, "./hmsk.keras", "./hanmi_sk_settings.ini", "모의투자")

strategy1.run()

#schedule.every().day.at("09:00").do(strategy1.run)

#while True:
#    schedule.run_pending()
#    time.sleep(1)