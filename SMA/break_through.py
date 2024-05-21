import backtest
import stockdata
import strategy
import threading

def calculate_profit(net_wealth, init_amount):
    return (net_wealth - init_amount) / init_amount

sma_window = 14
lma_window = 50
stocks = ["nvda", "meta", "msft", "tsla"]
init_amount = 1000000
units = []
threads = []
for stock in stocks:
    prices = stockdata.create_dataset([stock], stockdata.today_before(300), stockdata.today(), "1d")
    stgy = strategy.Strategy(prices, sma_window, lma_window)
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