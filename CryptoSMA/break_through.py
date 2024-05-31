import crypto_data
import backtest
import strategy1
import threading

def calculate_profit(net_wealth, init_amount):
    return (net_wealth - init_amount) / init_amount

sma_window = 10
lma_window = 30
stocks = ["BTC-USD"]
init_amount = 1000000
units = []
threads = []
for stock in stocks:
    prices = crypto_data.create_dataset([stock], crypto_data.today_before(50), crypto_data.today(), interval='15m')
    stgy = strategy1.Strategy(prices, sma_window, lma_window)
    units.append(backtest.BacktestUnit(stgy, init_amount / len(stocks)))
    threads.append(threading.Thread(target=units[-1].run))
    threads[-1].start()

for thread in threads:
    thread.join()

sum_net_wealth = 0
for unit in units:
    sum_net_wealth += unit.net_wealth[-1]

profit = calculate_profit(sum_net_wealth, init_amount)
print(profit)