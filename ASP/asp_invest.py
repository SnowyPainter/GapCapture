import schedule
import time
import invest
import os
import configparser
from datetime import datetime, timedelta
import pytz

def is_market_open(nyse):
    if nyse:
        tz = pytz.timezone('America/New_York')
    else:
        tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(tz)
    if nyse:
        return (now.hour == 9 and now.minute >= 30) or (9 < now.hour < 16) or (now.hour == 16 and now.minute == 0)
    else:
        return (now.hour == 9 and now.minute >= 0) or (9 < now.hour < 15) or (now.hour == 15 and now.minute <= 30)

def main():
    config = configparser.ConfigParser()
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
    start_time = "22:30" if symbol_nyse else "09:00"
    strategy1 = invest.ASPInvest(config['ACCOUNT']['APIKEY'], config['ACCOUNT']['APISECRET'], config['ACCOUNT']['ACCNO'], False, config['SETTINGS']['PATH'], af_nyse, symbol_nyse,"실전투자")

    if True:#is_market_open(symbol_nyse):
        strategy1.run()
    
    print("The log will be written at this directory.")

    schedule.every().day.at(start_time).do(strategy1.run)

    while True:
        schedule.run_pending()
        time.sleep(1)