import backtest
import stockdata
import strategy
import concurrent.futures

def calculate_profit(net_wealth, init_amount):
    return (net_wealth - init_amount) / init_amount

sma_window = 14
lma_window = 50
nvda_prices = stockdata.create_dataset(["nvda"], stockdata.today_before(300), stockdata.today(), "1d")
msft_prices = stockdata.create_dataset(["msft"], stockdata.today_before(300), stockdata.today(), "1d")
strategy_nvda = strategy.Strategy(nvda_prices, sma_window, lma_window)
strategy_msft = strategy.Strategy(msft_prices, sma_window, lma_window)

init_amount = 100000

nvda_unit = backtest.BacktestUnit(strategy_nvda, init_amount / 2)
msft_unit = backtest.BacktestUnit(strategy_msft, init_amount / 2)

with concurrent.futures.ThreadPoolExecutor() as executor:
    nuf = executor.submit(nvda_unit.test)
    tuf = executor.submit(msft_unit.test)
    
    profit = calculate_profit(nuf.result()[-1] + tuf.result()[-1], init_amount)
    print(profit)