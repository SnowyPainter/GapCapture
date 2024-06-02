import stockdata
import readini
import learn, backtest
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def is_six_digit_number(s):
    return s.isdigit() and len(s) == 6
def main(settings, amount):
    config = readini.read(settings)
    code1_is_digit = is_six_digit_number(config["CODE1"])
    code2_is_digit = is_six_digit_number(config["CODE2"])
    if code1_is_digit and code2_is_digit:
        symbol1 = str(config["CODE1"]) + "." + config["TAG1"]
        symbol2 = str(config["CODE2"]) + "." + config["TAG2"]
    elif not (code1_is_digit ^ code2_is_digit):
        symbol1 = str(config["CODE1"])
        symbol2 = str(config["CODE2"])
    else:
        print("쌍 매매하는 주식들은 같은 거래소 내에 있어야 합니다. 환전 문제")
        exit()

    env = learn.ASPEnvironment(symbol1, symbol2, config["AFFECTIVE"], stockdata.today_before(50), stockdata.today(),"5m")

    stgy = backtest.Strategy1(env, amount, 0.0025, config["MODEL"])
    stgy.run()
    print("Trades : ", stgy.trades)
    print("ASP System Contribution : ", (stgy.affective_system_profit_sum / stgy.net_wealths[-1]))
    print("End", (stgy.net_wealths[-1] - amount) / amount)
    print("Best ", (max(stgy.net_wealths) - amount) / amount)
    print("Worst ", (min(stgy.net_wealths) - amount) / amount)

    df = pd.DataFrame({"NetWealth":stgy.net_wealths, f"{env.affective_symbol}": env.raw[f"{env.affective_symbol}_Price"].iloc[len(env.raw[f"{env.affective_symbol}_Price"]) - len(stgy.net_wealths):]})
    mean, std = df.mean(), df.std()
    df = (df-mean) / std

    print("제3의 주식과의 연관성")
    print(df.corr())

    plt.plot(df["NetWealth"], label="Net Wealth")
    plt.plot(df[f"{env.affective_symbol}"], label=f"{env.affective_symbol} Price")
    plt.legend()
    plt.show()