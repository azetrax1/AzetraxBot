import ccxt
import asyncio
import pandas as pd
import json
import time
from colorama import Fore, Style
from strategies.rsi_macd import rsi_macd_signal
from strategies.volume_analyzer import volume_signal
from strategies.trend_detector import trend_signal
from strategies.combined_signal import combine_signals

# Config dosyasını oku
with open("config.json", "r") as f:
    config = json.load(f)

exchange = getattr(ccxt, config["exchange"])()

# 🔹 Binance'teki tüm USDT paritelerini al
def get_usdt_pairs():
    markets = exchange.load_markets()
    usdt_pairs = [symbol for symbol in markets if symbol.endswith("/USDT")]
    return usdt_pairs

# 🔹 Veri çekme
def fetch_data(symbol):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=config["timeframe"], limit=100)
        df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
        return df
    except Exception as e:
        print(Fore.RED + f"{symbol} verisi alınamadı: {e}" + Style.RESET_ALL)
        return None

# 🔹 Tek parite analizi
async def analyze(symbol):
    df = fetch_data(symbol)
    if df is None or df.empty:
        return

    rsi_macd = rsi_macd_signal(df, config["rsi_period"], config["macd_fast"], config["macd_slow"], config["macd_signal"])
    volume = volume_signal(df, config["volume_window"])
    trend = trend_signal(df)
    combined = combine_signals(rsi_macd, volume, trend)

    color = Fore.GREEN if "BUY" in combined else Fore.RED if "SELL" in combined else Fore.YELLOW
    print(f"{color}{symbol:<12} | RSI-MACD: {rsi_macd:<5} | Volume: {volume:<12} | Trend: {trend:<9} | Signal: {combined}{Style.RESET_ALL}")

# 🔹 Ana döngü
async def main():
    print(Fore.CYAN + "\n🚀 Binance Piyasa Taraması Başladı (Tüm USDT Çiftleri)...\n" + Style.RESET_ALL)
    usdt_pairs = get_usdt_pairs()
    print(Fore.MAGENTA + f"Toplam {len(usdt_pairs)} parite bulundu.\n" + Style.RESET_ALL)
    await asyncio.sleep(2)

    while True:
        batch_size = 10  # Aynı anda analiz edilecek parite sayısı
        for i in range(0, len(usdt_pairs), batch_size):
            batch = usdt_pairs[i:i + batch_size]
            tasks = [analyze(symbol) for symbol in batch]
            await asyncio.gather(*tasks)
            print(Fore.WHITE + f"\n--- {i+len(batch)} / {len(usdt_pairs)} parite tarandı ---\n" + Style.RESET_ALL)
            await asyncio.sleep(1)
        print(Fore.MAGENTA + "\n⏳ 60 saniye bekleniyor, döngü yeniden başlatılacak...\n" + Style.RESET_ALL)
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
