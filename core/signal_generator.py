from termcolor import colored

def generate_signal_with_context(df_short, df_long, symbol, df_scalp=None):
    try:
        last_short = df_short["close"].iloc[-1]
        last_long = df_long["close"].iloc[-1]

        momentum = "flat"
        if last_short > df_short["close"].iloc[-2]:
            momentum = "up"
        elif last_short < df_short["close"].iloc[-2]:
            momentum = "down"

        context = f"Sentiment: unknown | Momentum: {momentum}"

        if last_short > last_long:
            return "long", "long", "long", "scalp_long", context
        elif last_short < last_long:
            return "short", "short", "short", "scalp_short", context
        else:
            return "hold", "hold", "hold", "hold", context

    except Exception as e:
        print(f"⚠️ Signal generation failed: {e}")
        return "hold", "hold", "hold", "hold", "Error in signal generation"

def notify(symbol, signal, context=""):
    print(colored(f"📢 {symbol} | Signal: {signal.upper()} | {context}", "blue"))

