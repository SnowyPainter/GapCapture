import pandas as pd
import yfinance as yf
import pytz
from datetime import datetime, timedelta, time

import pprint

def today(tz = 'America/New_York'):
    return datetime.now(pytz.timezone(tz))
def today_before(day, tz = 'America/New_York'):
    return datetime.now(pytz.timezone(tz)) - timedelta(days=day)

def merge_dfs(dfs, on):
    merged = dfs[0]
    for i in range(1, len(dfs)):
        merged = merged.merge(dfs[i], on=on)
    return merged

def merge_without_on(df1, df2, nan_column):
    merged = df1.merge(df2, left_index=True, right_index=True, how='left')
    for i in range(1, (len(merged) if len(merged) <= len(df2) else len(df2))+1):
        merged[nan_column][-i] = df2[nan_column][-i]
    return merged

def get_realtime_price(ticker):
    t = yf.Ticker(ticker)
    return t.info.get('currentPrice')

def get_symbol_historical(symbol, start, end, period,interval):
    d = yf.download(symbol, start=start, end=end, period=period, interval=interval)
    d.rename(columns={'Open': symbol+'_Price'}, inplace=True)
    d.index = pd.to_datetime(d.index, format="%Y-%m-%d %H:%M:%S%z")
    d.dropna(inplace=True)
    return d[[symbol+'_Price']]

def create_dataset(symbols, affective_stock, start, end, interval):
    dfs = []
    for symbol in symbols:
        dfs.append(get_symbol_historical(symbol, start=start, end=end, period="max", interval=interval))
    merged = merge_dfs(dfs, on=dfs[0].index.name)
    df = get_symbol_historical(affective_stock, start=start, end=end, period="max", interval=interval)
    return merge_without_on(merged, df, affective_stock+"_Price")