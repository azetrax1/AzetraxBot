import numpy as np

def trend_signal(df):
    df["slope"] = np.gradient(df["close"])
    last = df.iloc[-5:]
    if all(last["slope"] > 0):
        return "UPTREND"
    elif all(last["slope"] < 0):
        return "DOWNTREND"
    return "SIDEWAYS"
