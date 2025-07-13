import pandas_ta as ta
import numpy as np

def generate_signal(df):
    df = df.copy()
    df.ta.macd(append=True)
    df.ta.rsi(append=True)
    df.ta.bbands(append=True)
    df.ta.supertrend(append=True)

    try:
        macd_hist = df['MACDh_12_26_9'].iloc[-1]
        rsi = df['RSI_14'].iloc[-1]
        rsi_prev = df['RSI_14'].iloc[-2]
        close = df['close'].iloc[-1]
        upper = df['BBU_20_2.0'].iloc[-1]
        lower = df['BBL_20_2.0'].iloc[-1]
        supertrend = df['SUPERT_7_3.0'].iloc[-1]
    except KeyError as e:
        print(f"Missing indicator data: {e}")
        return "hold"

    votes = []
    if macd_hist > 0:
        votes.append("long")
    elif macd_hist < 0:
        votes.append("short")

    if rsi < 30:
        votes.append("long")
    elif rsi > 70:
        votes.append("short")
    else:
        votes.append("hold")

    if close < lower:
        votes.append("long")
    elif close > upper:
        votes.append("short")
    else:
        votes.append("hold")

    if close > supertrend:
        votes.append("long")
    else:
        votes.append("short")

    final_signal = max(set(votes), key=votes.count)

    # Optional: print momentum reversal signal
    if rsi_prev < 30 and rsi > 40:
        print("🚨 RSI recovery — potential bullish reversal")
    elif rsi_prev > 70 and rsi < 60:
        print("🚨 RSI cooling — potential bearish reversal")

    return final_signal

def generate_signal_with_context(df_short, df_long):
    signal_short = generate_signal(df_short)
    signal_long = generate_signal(df_long)

    if signal_short == signal_long:
        final = signal_short
        context = "✅ CONFIRMED TREND"
    elif signal_short == "long" and signal_long == "short":
        final = "hold"
        context = "⚠️ BULLISH SENTIMENT SHIFT DETECTED"
    elif signal_short == "short" and signal_long == "long":
        final = "hold"
        context = "⚠️ BEARISH SENTIMENT SHIFT DETECTED"
    else:
        final = "hold"
        context = "🤔 UNCERTAIN SIGNAL — HOLD"

    return final, signal_short, signal_long, context

def notify(symbol, primary_signal, context="", scalp_signal=None):
    icons = {
        "long": "🟢",
        "short": "🔴",
        "hold": "⚪",
        "scalp_long": "🟢⚡",
        "scalp_short": "🔴⚡"
    }

    icon_primary = icons.get(primary_signal, "❔")
    icon_scalp = icons.get(scalp_signal, "") if scalp_signal else ""

    output = f"{icon_primary} [{symbol}] Action: {primary_signal.upper()}"
    if scalp_signal:
        output += f" | Scalp: {scalp_signal.upper()} {icon_scalp}"
    if context:
        output += f" | {context}"

    print(output)
