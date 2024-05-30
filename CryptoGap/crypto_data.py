import pandas as pd
import yfinance as yf
import pytz
from datetime import datetime, timedelta, time

def today(tz = 'America/New_York'):
    return datetime.now(pytz.timezone(tz))
def today_before(day, tz = 'America/New_York'):
    return datetime.now(pytz.timezone(tz)) - timedelta(days=day)

def merge_dfs(dfs, on):
    merged = dfs[0]
    for i in range(1, len(dfs)):
        merged = merged.merge(dfs[i], on=on)
    return merged

def get_realtime_price(symbol):
    d = yf.download(symbol, start=today(), end=today())
    d.rename(columns={'Close': symbol}, inplace=True)
    return d[symbol]

def get_symbol_historical(symbol, start, end, period,interval):
    d = yf.download(symbol, start=start, end=end, period=period, interval=interval)
    d.rename(columns={'Open': symbol}, inplace=True)
    d.index = pd.to_datetime(d.index, format="%Y-%m-%d %H:%M:%S%z")
    d.dropna(inplace=True)
    return d[[symbol]]

def create_dataset(symbols, start, end, interval):
    dfs = []
    for symbol in symbols:
        dfs.append(get_symbol_historical(symbol, start=start, end=end, period="max", interval=interval))
    return merge_dfs(dfs, on=dfs[0].index.name)