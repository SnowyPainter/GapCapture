import sys
sys.path.append('..')
import strategy
import stockdata
import math
import theme_stock_data

symbols = ["tsla", "msft", "nvda"] #theme_stock_data.semiconductor()
df = stockdata.create_dataset(symbols, start=stockdata.today_before(50), end=stockdata.today(), interval="5m")
stgy = strategy.Strategy(df)

def buy(current_amount, amount, price):
    if current_amount > amount:
        unit = math.floor((amount * 0.9975) / price)
    else:
        unit = math.floor((current_amount * 0.9975) / price)
    return unit * price, unit
def sell(units, price):
    return units * price

units = {}
for symbol in symbols:
    units[symbol] = 0

init_amount = 10000000
current_amount = init_amount
installment_amount = init_amount / 5

for i in range(0, len(df) - 60):
    action_result, prices = stgy.action()
    for stock_to_buy in action_result[strategy.BUY]:
        stock = stock_to_buy.replace('_Price', '')
        amount, u = buy(current_amount, installment_amount, prices[stock_to_buy])
        current_amount -= amount
        units[stock] += u
    for stock_to_sell in action_result[strategy.SELL]:
        stock = stock_to_sell.replace('_Price', '')
        current_amount += sell(units[stock], prices[stock_to_sell])
        units[stock] = 0
        
total_evaluate = current_amount
for symbol in symbols:
    total_evaluate += units[symbol] * prices[symbol+'_Price']
    
print((total_evaluate - init_amount) / init_amount)