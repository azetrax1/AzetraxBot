import ccxt
import pandas as pd
import ta
import json
from strategies.rsi_macd import rsi_macd_signal
from strategies.volume_analyzer import volume_signal
from strategies.trend_detector import trend_signal
from strategies.combined_signal import combine_signals

with open("config.json", "r") as f:
    config = json.load(f)

exchange = getattr(ccxt, config["exchange"])()

def backtest(symbol, limit=500):
    bars = exchange.fetch_ohlcv(symbol, timeframe=config["timeframe"], limit=limit)
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])

    balance = 1000  # USDT başlangıç
    position = None
    entry = 0

    for i in range(50, len(df)):
        subset = df.iloc[:i]
        rsi_macd = rsi_macd_signal(subset, config["rsi_period"], config["macd_fast"], config["macd_slow"], config["macd_signal"])
        volume = volume_signal(subset, config["volume_window"])
        trend = trend_signal(subset)
        signal = combine_signals(rsi_macd, volume, trend)

        price = subset.iloc[-1]["close"]

        if "BUY" in signal and position is None:
            position = "LONG"
            entry = price
        elif "SELL" in signal and position == "LONG":
            profit = (price - entry) / entry * 100
            balance *= (1 + profit / 100)
            position = None

    print(f"{symbol} için son bakiye: {balance:.2f} USDT")

if __name__ == "__main__":
    backtest("BTC/USDT")
