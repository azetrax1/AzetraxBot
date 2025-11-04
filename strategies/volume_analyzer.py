def volume_signal(df, window):
    df["avg_volume"] = df["volume"].rolling(window=window).mean()
    last = df.iloc[-1]
    if last["volume"] > 1.5 * last["avg_volume"]:
        return "HIGH_VOLUME"
    return "NORMAL"
