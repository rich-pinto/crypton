import pandas as pd
import time
from core.fetch_data import fetch_ohlcv
from core.signal_generator import generate_signal_with_context, notify
from core.scalp_advisor import analyze_scalp_opportunity

symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT"]
timeframes = {"scalp": "1m", "short": "15m", "long": "1h"}

print("📈 Starting crypto signal bot with scalp mode enabled...")

while True:
    for symbol in symbols:
        print(f"🔎 Analyzing {symbol}")
        try:
            df_scalp = fetch_ohlcv(symbol, timeframe=timeframes["scalp"], limit=100)
            df_short = fetch_ohlcv(symbol, timeframe=timeframes["short"], limit=100)
            df_long = fetch_ohlcv(symbol, timeframe=timeframes["long"], limit=100)

            # Run scalp analysis
            scalp_advice, scalp_reason = analyze_scalp_opportunity(df_scalp, symbol)

            # Run trend signal analysis
            result = generate_signal_with_context(df_short, df_long, symbol, df_scalp)

            if isinstance(result, tuple) and len(result) >= 4:
                final_signal, signal_short, signal_long, scalp_signal, context = result[:5]
                print(f"⚪ [{symbol}] Action: {final_signal.upper()} | ✅ CONFIRMED | {context}")
                if (final_signal == "long" and scalp_signal == "scalp_long") or \
                   (final_signal == "short" and scalp_signal == "scalp_short"):
                    notify(symbol, scalp_signal, context)
                else:
                    notify(symbol, final_signal, context)
            else:
                final_signal, _, _, context = result
                notify(symbol, final_signal, context)

        except Exception as e:
            print(f"⚠️ Error analyzing {symbol}: {e}")
    print("🔁 Waiting 60 seconds before next update...\n")
    time.sleep(60)

