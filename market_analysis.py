import requests
import pandas as pd
from ta import add_all_ta_features
from config import COINGECKO_API, DEXSCREENER_API, ARBISCAN_API, ARBISCAN_API_KEY

def get_market_data(token_id="bitcoin"):
    """دریافت داده‌های بازار از CoinGecko"""
    url = f"{COINGECKO_API}/coins/{token_id}/market_chart?vs_currency=usd&days=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
        return prices, volumes
    except requests.RequestException as e:
        print(f"خطا در دریافت داده از CoinGecko: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_dexscreener_data(token_address):
    """دریافت داده‌های توکن از DexScreener"""
    url = f"{DEXSCREENER_API}/tokens/{token_address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # فرض می‌کنیم داده‌های حجم و نقدینگی در پاسخ موجود است
        volume = data.get("volume", {}).get("h24", 0)  # حجم معاملات 24 ساعته
        liquidity = data.get("liquidity", {}).get("usd", 0)  # نقدینگی به دلار
        return {"volume": volume, "liquidity": liquidity}
    except requests.RequestException as e:
        print(f"خطا در دریافت داده از DexScreener: {e}")
        return {"volume": 0, "liquidity": 0}

def get_whale_transactions(token_address):
    """دریافت تراکنش‌های نهنگ‌ها از Arbiscan"""
    url = f"{ARBISCAN_API}?module=account&action=tokentx&contractaddress={token_address}&sort=desc&apikey={ARBISCAN_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        transactions = data.get("result", [])
        # فیلتر تراکنش‌های بزرگ (مثلاً بالای 1e18 wei یا معادل 1 واحد توکن)
        whale_txs = [tx for tx in transactions if float(tx.get("value", 0)) > 1e18]
        return whale_txs
    except requests.RequestException as e:
        print(f"خطا در دریافت داده از Arbiscan: {e}")
        return []

def analyze_token(token_id, token_address):
    """تحلیل توکن با ترکیب داده‌های CoinGecko، DexScreener و Arbiscan"""
    # دریافت داده‌های بازار
    prices, volumes = get_market_data(token_id)
    if prices.empty or volumes.empty:
        return {"token": token_id, "score": 0, "price": 0, "exit_points": []}

    # افزودن شاخص‌های تکنیکال
    prices = add_all_ta_features(prices, open="price", high="price", low="price", close="price", volume=volumes["volume"])

    # دریافت داده‌های DexScreener
    dexscreener_data = get_dexscreener_data(token_address)
    volume_score = 20 if dexscreener_data["volume"] > 1e6 else 0  # امتیاز برای حجم بالا
    liquidity_score = 20 if dexscreener_data["liquidity"] > 1e6 else 0  # امتیاز برای نقدینگی بالا

    # دریافت تراکنش‌های نهنگ‌ها از Arbiscan
    whale_txs = get_whale_transactions(token_address)
    whale_score = len(whale_txs) * 5  # هر تراکنش بزرگ 5 امتیاز

    # امتیازدهی کلی
    score = 30  # امتیاز پایه
    if prices["trend_macd"].iloc[-1] > 0:  # سیگنال صعودی MACD
        score += 20
    score += volume_score + liquidity_score + min(whale_score, 30)  # محدود کردن امتیاز نهنگ‌ها

    return {
        "token": token_id,
        "score": min(score, 100),
        "price": prices["price"].iloc[-1],
        "exit_points": [prices["price"].iloc[-1] * 1.1, prices["price"].iloc[-1] * 0.9]  # 10% سود/زیان
    }
