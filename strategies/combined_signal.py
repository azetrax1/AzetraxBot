def combine_signals(rsi_macd, volume, trend):
    scores = {"BUY": 1, "SELL": -1, "HOLD": 0}
    base = scores.get(rsi_macd, 0)

    if volume == "HIGH_VOLUME":
        base *= 1.2
    if trend == "UPTREND" and base > 0:
        base *= 1.3
    elif trend == "DOWNTREND" and base < 0:
        base *= 1.3

    if base >= 1:
        return "STRONG BUY"
    elif base <= -1:
        return "STRONG SELL"
    return "NEUTRAL"
