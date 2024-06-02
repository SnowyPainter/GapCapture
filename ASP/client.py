import sys
sys.path.append('..')

import schedule
import time
import invest
from KEYS import *
import os
import configparser

config = configparser.ConfigParser()

# 파일로 저장


if not os.path.exists('./keys.ini'):
    print("현재 위치의 keys.ini에 API키, API 시크릿, 계좌번호를 입력해주세요.")
    print("keys.ini 파일이 생성되었습니다.")
    config['ACCOUNT'] = {
        'APIKEY': 'API키를 입력해주세요',
        'APISECRET': 'API시크릿키를 입력해주세요',
        'ACCNO': '게좌번호를 입력해주세요(끝자리 01)'
    }
    config['SETTINGS'] = {
        'PATH': 'settings.ini 파일 경로를 입력해주세요'
    }
    config['STOCK'] = {
        'IsAffectiveNyse' : '참조할 제3의 주식이 미국주식인가요? (yes/no)',
        'IsSymbolsNyse' : '거래할 주식 쌍들이 미국주식인가요? (yes/no)'
    }
    with open('keys.ini', 'w') as configfile:
        config.write(configfile)
    exit()

config.read("./keys.ini")

af_nyse = config['STOCK']['IsAffectiveNyse'] == 'yes'
symbol_nyse = config['STOCK']['IsSymbolsNyse'] == 'yes'

strategy1 = invest.ASPInvest(config['ACCOUNT']['APIKEY'], config['ACCOUNT']['APISECRET'], config['ACCOUNT']['ACCNO'], False, config['SETTINGS']['PATH'], af_nyse, symbol_nyse,"실전투자")

strategy1.run()

print("This program run investing algorithm every 22:00")
print("The log will be written at this directory.")

schedule.every().day.at("09:00").do(strategy1.run)

while True:
    schedule.run_pending()
    time.sleep(1)