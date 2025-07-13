import ccxt
import pandas as pd

exchange = ccxt.binance()

def fetch_ohlcv(symbol, timeframe="1m", limit=100):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        print(f"⚠️ Error fetching OHLCV data for {symbol}: {e}")
        return pd.DataFrame()

