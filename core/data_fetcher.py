# core/data_fetcher.py

import ccxt
import pandas as pd

exchange = ccxt.binance()

def fetch_candles(symbol, timeframe='15m', limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df
