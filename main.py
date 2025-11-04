import os
import sys
import subprocess
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# ====== OTO SANAL ORTAM KURULUMU ======
venv_path = Path("venv")

def ensure_virtualenv():
    """Venv yoksa oluşturur ve gerekli kütüphaneleri yükler."""
    if not venv_path.exists():
        print("🔧 Sanal ortam (venv) oluşturuluyor...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✅ Sanal ortam oluşturuldu.")

    # Windows'ta aktif hale getirme komutu
    if os.name == "nt":
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"

    # Gerekli kütüphaneler
    required = ["python-binance", "pandas", "numpy", "requests", "matplotlib"]
    for pkg in required:
        subprocess.check_call([str(pip_path), "install", pkg])

    print("✅ Gerekli kütüphaneler yüklendi.")
    return python_path


# Eğer aktif ortam değilse, otomatik yeniden çalıştır
if not hasattr(sys, 'real_prefix') and not (venv_path / "Scripts").exists():
    python_path = ensure_virtualenv()
    print("🚀 Bot, sanal ortam içinde yeniden başlatılıyor...")
    subprocess.check_call([str(python_path), __file__])
    sys.exit(0)


# ====== BİNANCE ANALİZ BOTU ======
from binance.client import Client
from binance.exceptions import BinanceAPIException

# 🔑 KENDİ BİLGİLERİNİ BURAYA GİR
API_KEY = "BINANCE_API_KEYIN"
API_SECRET = "BINANCE_SECRET_KEYIN"
TELEGRAM_TOKEN = "TELEGRAM_BOT_TOKENIN"
CHAT_ID = "TELEGRAM_CHAT_IDIN"

TIMEFRAME = "15m"
LIMIT = 500
CHECK_INTERVAL = 60

client = Client(API_KEY, API_SECRET)

# ====== TELEGRAM BİLDİRİM ======
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram hatası: {e}")


# ====== TEKNİK ANALİZ ======
def get_klines(symbol, interval, limit):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except BinanceAPIException as e:
        print(f"{symbol} verisi alınamadı: {e}")
        return None


def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(data):
    ema12 = data['close'].ewm(span=12, adjust=False).mean()
    ema26 = data['close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal


def analyze_symbol(symbol):
    df = get_klines(symbol, TIMEFRAME, LIMIT)
    if df is None or len(df) < 50:
        return None

    df['rsi'] = calculate_rsi(df)
    df['macd'], df['signal'] = calculate_macd(df)

    rsi = df['rsi'].iloc[-1]
    macd = df['macd'].iloc[-1]
    signal = df['signal'].iloc[-1]

    if rsi < 30 and macd > signal:
        return f"📈 STRONG BUY sinyali! {symbol} RSI={rsi:.2f}"
    elif rsi > 70 and macd < signal:
        return f"📉 STRONG SELL sinyali! {symbol} RSI={rsi:.2f}"
    return None


def get_all_symbols():
    tickers = client.get_all_tickers()
    return [t['symbol'] for t in tickers if t['symbol'].endswith('USDT')]


def main():
    symbols = get_all_symbols()
    print(f"{len(symbols)} adet USDT paritesi taranacak...")

    while True:
        for symbol in symbols:
            signal = analyze_symbol(symbol)
            if signal:
                print(signal)
                send_telegram_message(signal)
        print("Tüm pariteler tarandı. Yeniden tarama bekleniyor...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    print("🚀 Advenge Analyzer başlatılıyor...")
    main()
