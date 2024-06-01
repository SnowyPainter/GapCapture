import stockdata
import tensorflow as tf
import numpy as np 
import math

MAX_UNITS = 120

def reshape(state):
    return np.reshape(state, [1, 1, 3])
def get_units_of_sell(curr_units):
    n = curr_units
    if n > MAX_UNITS:
        n = MAX_UNITS
    return n
def get_units_of_buy(current_balance, stock_price):
    n = math.floor(current_balance / stock_price)
    if n > MAX_UNITS:
        n = MAX_UNITS
    return n

def sell(units, price, fee):
    return units * price * (1-fee)
def buy(units, price, fee):
    return units * price * (1+fee)

class Strategy1:
    
    def set_affective_entry_price(self, price):
        self.affective_entry_price += price
        self.affective_entry_price /= (1 if self.affective_entry_price == 0 else 2)
    def set_entry_price_symbol1(self, units, new_prices):
        self.entry_price_symbol1 += units * new_prices
        self.entry_price_symbol1 /= (1 if self.entry_price_symbol1 == 0 else (units + 1))
    def set_entry_price_symbol2(self, units, new_prices):
        self.entry_price_symbol2 += units * new_prices
        self.entry_price_symbol2 /= (1 if self.entry_price_symbol2 == 0 else (units + 1))

    def __init__(self, env, amount, fee, model):
        self.agent = tf.keras.models.load_model(model)
        self.env = env
        self.amount = amount
        self.fee = fee
    
    def get_price(self, bar):
        prices = self.env.raw.iloc[bar]
        prices = np.array(prices)
        #prices[1] /= 1250 # currency ratio
        return prices
    
    def run(self):
        self.units = 0
        self.position = 0
        self.trades = 0
        self.net_wealths = list()
        bar = 1
        self.current_balance = self.amount
        self.symbol1_units = 0
        self.symbol2_units = 0
        
        self.entry_price_symbol1 = 0
        self.entry_price_symbol2 = 0
        prices = self.get_price(bar)
        self.affective_entry_price = prices[2]
        refresh_affective_entry = 24
        
        self.affective_system_profit_sum = 0
        self.affective_system_buy = 0
        self.affective_system_sell = 0
        
        no_sell = True
        no_buy = False
        
        while bar < len(self.env.normalized_data) - 1:
            prices = self.get_price(bar)
            state = reshape(np.array([self.env.get_state(bar)]))
            action = np.argmax(self.agent.predict(state, verbose=0)[0, 0])
            # if 1
            # symbol 2 sell, symbol 1 buy
            # if 2
            # symbol 2 buy, symbol 1 sell
            # if 0 -> hold
            
            if bar % refresh_affective_entry == 0:
                self.set_affective_entry_price(prices[2])
            
            symbol1_loss = ((prices[0] - self.entry_price_symbol1) / self.entry_price_symbol1) if self.entry_price_symbol1 != 0 else 0
            symbol2_loss = ((prices[1] - self.entry_price_symbol2) / self.entry_price_symbol2) if self.entry_price_symbol2 != 0 else 0
            affective_loss = ((prices[2] - self.affective_entry_price) / self.affective_entry_price) if self.affective_entry_price != 0 else 0
            
            if not no_sell:
                if affective_loss < -0.02:
                    units = get_units_of_sell(self.symbol1_units)
                    if units > 0:
                        print(f"affective low sell {symbol1_loss}")
                        self.symbol1_units -= units
                        profit = sell(units, prices[0], self.fee)
                        self.affective_system_profit_sum += profit
                        self.affective_system_sell += 1
                        self.current_balance += profit
                        self.trades += 1
                    units = get_units_of_sell(self.symbol2_units)
                    if units > 0:
                        print(f"affective low sell {symbol2_loss}")
                        self.symbol2_units -= units
                        profit = sell(units, prices[1], self.fee)
                        self.affective_system_profit_sum += profit
                        self.affective_system_sell += 1
                        self.current_balance += profit
                        self.trades += 1
            if not no_buy:
                if affective_loss > 0.02:
                    units = get_units_of_buy(self.current_balance, prices[0])
                    if units > 0:
                        self.set_affective_entry_price(prices[2])
                        self.set_entry_price_symbol1(units, prices[0])
                        print(f"affective high buy")
                        self.symbol1_units += units
                        cost = buy(units, prices[0], self.fee)
                        self.affective_system_profit_sum -= cost
                        self.current_balance -= cost
                        self.affective_system_buy += 1
                        self.trades += 1
                    units = get_units_of_buy(self.current_balance, prices[1])
                    if units > 0:
                        self.set_affective_entry_price(prices[2])
                        self.set_entry_price_symbol1(units, prices[1])
                        print(f"affective high buy")
                        self.symbol2_units += units
                        cost = buy(units, prices[1], self.fee)
                        self.affective_system_profit_sum -= cost
                        self.current_balance -= cost 
                        self.affective_system_buy += 1
                        self.trades += 1

            if self.symbol1_units > 0:
                units = get_units_of_sell(self.symbol1_units)
                if symbol1_loss > 0.035: #tp
                    print(f"이익 초과 symbol1 {units} / {symbol1_loss} 매도")
                    self.symbol1_units -= units
                    profit = sell(units, prices[0], self.fee)
                    self.current_balance += profit
                    self.trades += 1
                    if self.affective_system_buy > 0:
                        self.affective_system_profit_sum += profit
                        self.affective_system_sell += 1
                elif symbol1_loss < -0.045 and False:
                    print(f"손절 symbol1 {units} / {symbol1_loss} 매도")
                    self.symbol1_units -= units
                    profit = sell(units, prices[0], self.fee)
                    self.current_balance += profit 
                    self.trades += 1
                    if self.affective_system_buy > 0:
                        self.affective_system_profit_sum += profit
                        self.affective_system_sell += 1
            if self.symbol2_units > 0:
                units = get_units_of_sell(self.symbol2_units)
                if symbol2_loss > 0.035:
                    print(f"이익 초과 symbol2 {units} / {symbol2_loss} 매도")
                    self.symbol2_units -= units
                    profit = sell(units, prices[1], self.fee)
                    self.trades += 1
                    self.current_balance += profit
                    if self.affective_system_buy > 0:
                        self.affective_system_profit_sum += profit
                        self.affective_system_sell += 1
                elif symbol2_loss < -0.05 and False:
                    print(f"손절 symbol2 {units} / {symbol2_loss} 매도")
                    self.symbol2_units -= units
                    profit = sell(units, prices[1], self.fee)
                    self.trades += 1
                    self.current_balance += profit
                    if self.affective_system_buy > 0:
                        self.affective_system_profit_sum += profit
                        self.affective_system_sell += 1
            if action == 0:
                print(f"홀딩 {self.current_balance}, {prices}")
            if action != 0:
                if action == 1:
                    if self.symbol2_units > 0:
                        units = get_units_of_sell(self.symbol2_units)
                        print(f"symbol2 {units} 매도 {self.current_balance}")
                        self.symbol2_units -= units
                        self.trades += 1
                        profit = sell(units, prices[1], self.fee)
                        if self.affective_system_buy > 0:
                            self.affective_system_profit_sum += profit
                            self.affective_system_sell += 1
                        self.current_balance += profit
                        if self.symbol2_units <= 0:
                            self.entry_price_symbol2 = 0
                    units = get_units_of_buy(self.current_balance, prices[0])
                    if units > 0:
                        self.set_affective_entry_price(prices[2])
                        self.set_entry_price_symbol1(units, prices[0])
                        self.trades += 1
                        print(f"symbol1 {units} 매수 {self.current_balance} 평단 : {self.entry_price_symbol1}")
                        cost = buy(units, prices[0], self.fee)
                        self.symbol1_units += units
                        if self.affective_system_sell > 0 and self.affective_system_buy > self.affective_system_sell:
                            self.affective_system_profit_sum -= cost
                            self.affective_system_buy += 1
                        self.current_balance -= cost 
                        
                elif action == 2:
                    if self.symbol1_units > 0:
                        units = get_units_of_sell(self.symbol1_units)
                        print(f"symbol1 {units} 매도 {self.current_balance}")
                        self.symbol1_units -= units
                        self.trades += 1
                        profit = sell(units, prices[0], self.fee)
                        self.current_balance += profit 
                        if self.affective_system_buy > 0:
                            self.affective_system_profit_sum += profit
                            self.affective_system_sell += 1
                        if self.symbol1_units <= 0:
                            self.entry_price_symbol1 = 0
                    units = get_units_of_buy(self.current_balance, prices[1])
                    if units > 0:
                        self.set_affective_entry_price(prices[2])
                        self.set_entry_price_symbol2(units, prices[1])
                        self.trades += 1
                        print(f"symbol2 {units} 매수 {self.current_balance} 평단 : {self.entry_price_symbol2}")
                        self.symbol2_units += units
                        cost = buy(units, prices[1], self.fee)
                        self.current_balance -= cost
                        if self.affective_system_sell > 0 and self.affective_system_buy > self.affective_system_sell:
                            self.affective_system_profit_sum -= cost
                            self.affective_system_buy += 1
            
            nw = self.symbol1_units * prices[0] + self.symbol2_units * prices[1] + self.current_balance
            #print(nw)
            self.net_wealths.append(nw)
            self.units = self.symbol1_units + self.symbol2_units
            #print("AFFECTIVE SYSTEM PROFIT SUM : ", self.affective_system_profit_sum)
            #print(self.affective_system_buy, self.affective_system_sell)
            bar += 1
            
        remain =  self.affective_system_buy - self.affective_system_sell
        if remain > 0:
            self.affective_system_profit_sum += (self.symbol1_units * prices[0] + self.symbol2_units * prices[1])
        #print("AFFECTIVE SYSTEM PROFIT SUM : ", self.affective_system_profit_sum)