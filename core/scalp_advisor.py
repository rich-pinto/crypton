import pandas as pd
import pandas_ta as ta
import json
from datetime import datetime
from termcolor import colored
import ccxt

OUTPUT_PATH = "/var/www/html/crypto-signals/signals.json"
exchange = ccxt.binance()

def write_signal_to_file(symbol, signal, reason):
    signal_data = {
        "symbol": symbol,
        "signal": signal,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        with open(OUTPUT_PATH, "a") as f:
            f.write(json.dumps(signal_data) + "\n")
    except Exception as e:
        print(colored(f"❌ Failed to write signal to file: {e}", "red"))

def fetch_ohlcv(symbol, timeframe="1m", limit=100):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        print(colored(f"⚠️ Error fetching OHLCV for {symbol}: {e}", "red"))
        return pd.DataFrame()

def analyze_scalp_opportunity(df, symbol=None):
    if df is None or df.empty:
        print(colored("⛔ Not ideal for scalping: No data", "red"))
        if symbol:
            write_signal_to_file(symbol, "hold", "No data")
        return "hold", "No data"

    df['ema_fast'] = ta.ema(df['close'], length=5)
    df['ema_slow'] = ta.ema(df['close'], length=13)
    df['rsi'] = ta.rsi(df['close'], length=14)

    stochrsi_df = ta.stochrsi(df['close'], length=14)
    if isinstance(stochrsi_df, pd.DataFrame):
        df = df.join(stochrsi_df)

    bb = ta.bbands(df['close'], length=20, std=2.0)
    df = df.join(bb)

    recent = df.iloc[-1]

    avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
    volume_spike = recent['volume'] > 1.2 * avg_volume

    if recent['ema_fast'] > recent['ema_slow'] and recent['close'] > recent['BBU_20_2.0'] and volume_spike:
        message = "Breakout above resistance with volume spike"
        print(colored(f"✅ Scalping LONG is favorable: {message}", "cyan"))
        if symbol:
            write_signal_to_file(symbol, "long", message)
        return "long", message

    if recent['ema_fast'] < recent['ema_slow'] and recent['close'] < recent['BBL_20_2.0'] and volume_spike:
        message = "Breakdown below support with volume spike"
        print(colored(f"✅ Scalping SHORT is favorable: {message}", "magenta"))
        if symbol:
            write_signal_to_file(symbol, "short", message)
        return "short", message

    if 'STOCHRSIk_14_14_3_3' in df.columns:
        if recent['rsi'] > 70 and recent['STOCHRSIk_14_14_3_3'] > 80:
            message = "Overbought conditions"
            print(colored(f"⚠️ Scalping SHORT due to {message}", "magenta"))
            if symbol:
                write_signal_to_file(symbol, "short", message)
            return "short", message

        if recent['rsi'] < 30 and recent['STOCHRSIk_14_14_3_3'] < 20:
            message = "Oversold conditions"
            print(colored(f"⚠️ Scalping LONG due to {message}", "cyan"))
            if symbol:
                write_signal_to_file(symbol, "long", message)
            return "long", message

    reasons = []
    if recent['ema_fast'] <= recent['ema_slow']:
        reasons.append("No EMA crossover")
    if recent['close'] <= recent.get('BBU_20_2.0', recent['close']):
        reasons.append("Not above resistance")
    if recent['close'] >= recent.get('BBL_20_2.0', recent['close']):
        reasons.append("Not below support")
    if not volume_spike:
        reasons.append("No volume spike")
    if 'STOCHRSIk_14_14_3_3' in df.columns:
        if not (recent['rsi'] > 70 and recent['STOCHRSIk_14_14_3_3'] > 80):
            reasons.append("Not overbought")
        if not (recent['rsi'] < 30 and recent['STOCHRSIk_14_14_3_3'] < 20):
            reasons.append("Not oversold")

    reason_str = ", ".join(reasons) if reasons else "Conditions not met"
    print(colored(f"⛔ Not ideal for scalping: {reason_str}", "red"))
    if symbol:
        write_signal_to_file(symbol, "hold", reason_str)
    return "hold", reason_str

if __name__ == "__main__":
    import sys
    default_symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT"]

    if len(sys.argv) == 2:
        input_symbol = sys.argv[1].upper()
        df = fetch_ohlcv(input_symbol, timeframe="1m", limit=100)
        analyze_scalp_opportunity(df, input_symbol)
    else:
        for symbol in default_symbols:
            df = fetch_ohlcv(symbol, timeframe="1m", limit=100)
            analyze_scalp_opportunity(df, symbol)
