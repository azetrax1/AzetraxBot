import ta

def rsi_macd_signal(df, rsi_period, macd_fast, macd_slow, macd_signal):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=rsi_period).rsi()
    macd = ta.trend.MACD(df["close"], window_fast=macd_fast, window_slow=macd_slow, window_sign=macd_signal)
    df["macd"], df["signal"] = macd.macd(), macd.macd_signal()

    last = df.iloc[-1]
    if last["rsi"] < 30 and last["macd"] > last["signal"]:
        return "BUY"
    elif last["rsi"] > 70 and last["macd"] < last["signal"]:
        return "SELL"
    return "HOLD"
