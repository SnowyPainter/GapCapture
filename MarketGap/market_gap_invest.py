import sys
sys.path.append('..')

import invest
from KEYS import *

strategy1 = invest.GapInvest(KEY, APISECRET, ACCOUNT_NO, True, "./hmsk.keras", "모의투자")

strategy1.run()