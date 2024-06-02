import os, configparser
import ASP.asp_invest as asp_invest, nyse_train, run_backtest, train

choices_list = ["해외주식 학습", "국내주식 학습", "백테스팅 하기", "실전투자 실행", "세팅 파일 만들기"]
i = 1
for t in choices_list:
    print(f"{i}. {t}")
    i+=1

choice = int(input("번호를 입력해주세요 : "))
if choice == 5: #세팅 파일 만들기
    t = input("모델이 필요합니다. 모델명은 종목1종목2.keras 입니다. 있으십니까? (yes/no) : ")
    if t != "yes":
        exit()
    print("모델명을 알고계신가요? 학습시킨 후 models 폴더에 있습니다.")
    
    affective = input("참조할 종목 코드 : ")
    bt = input("ASP System 구매 임계값(0.1 ~ 0.5) : ")
    st = input("ASP System 판매 임계값(-0.1 ~ -0.3) : ")
    model = input("모델 주소(예: ./models/nvdaamd.keras) : ")
    sa = input("한번에 최대 몇 개씩 팔까요? : ")
    ba = input("한번에 최대 몇 개씩 살까요? : ")
    code1 = input("종목코드1 : ")
    tag1 = input("종목태그1(코스피 KS, 코스닥 KQ, 해외주식은 입력하지 마세요) : ")
    name1 = input("종목명 : ")
    code2 = input("종목코드2 : ")
    tag2 = input("종목태그2(코스피 KS, 코스닥 KQ, 해외주식은 입력하지 마세요) : ")
    name2 = input("종목명 : ")
    tp = input("익절(예: 0.02, 2% 의미) : ")
    sl = input("손절(예: -0.02, -2% 의미) : ")
    config = configparser.ConfigParser()
    config['AFFECTIVE'] = {
       "CODE": affective,
       "BT": bt,
       "ST": st
    }
    config['MODEL'] = {
       "PATH":model
    }
    config['SETTINGS'] = {
        "SELL_AMOUNT": sa,
        "BUY_AMOUNT" : ba,
        "SYMBOL1" : code1,
        "SYMBOL1_NAME": name1,
        "SYMBOL1_TAG": tag1,
        "SYMBOL2": code2,
        "SYMBOL2_NAME": name2,
        "SYMBOL2_TAG": tag2,
        "FEE": 0.0025,
        "TAKE_PROFIT": tp,
        "STOP_LOSS": sl
    }
    with open(f'{code1}_{code2}_settings.ini', 'w') as configfile:
        config.write(configfile)

settings = input("세팅 파일의 위치를 입력해주세요 (예: ./sk_hanmi_settings.ini) : ")
if choice == 1: #해외주식 학습
    nyse_train.main(settings)
elif choice == 2: #국내주식 학습
    train.main(settings)
elif choice == 3: #백테스팅
    amount = int(input("소수 제외 초기 자본금을 입력해주세요. : "))
    run_backtest.main(settings, amount)
elif choice == 4: #실전투자
    asp_invest.main()