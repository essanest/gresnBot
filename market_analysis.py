import os
import requests
import pandas as pd
from ta import add_all_ta_features
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

class MarketAnalyzer:
    def __init__(self):
        self.COINGECKO_API = os.getenv("COINGECKO_API")
        self.DEXSCREENER_API = os.getenv("DEXSCREENER_API")
        self.ARBISCAN_API = os.getenv("ARBISCAN_API")
        self.ARBISCAN_API_KEY = os.getenv("ARBISCAN_API_KEY")

    def get_market_data(self, token_id="bitcoin"):
        """دریافت داده‌های بازار از CoinGecko"""
        url = f"{self.COINGECKO_API}/coins/{token_id}/market_chart?vs_currency=usd&days=1"
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

    def get_dexscreener_data(self, token_address):
        """دریافت داده‌های توکن از DexScreener"""
        url = f"{self.DEXSCREENER_API}/tokens/{token_address}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            volume = data.get("volume", {}).get("h24", 0)
            liquidity = data.get("liquidity", {}).get("usd", 0)
            return {"volume": volume, "liquidity": liquidity}
        except requests.RequestException as e:
            print(f"خطا در دریافت داده از DexScreener: {e}")
            return {"volume": 0, "liquidity": 0}

    def get_whale_transactions(self, token_address):
        """دریافت تراکنش‌های نهنگ‌ها از Arbiscan"""
        url = f"{self.ARBISCAN_API}?module=account&action=tokentx&contractaddress={token_address}&sort=desc&apikey={self.ARBISCAN_API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            transactions = data.get("result", [])
            whale_txs = [tx for tx in transactions if float(tx.get("value", 0)) > 1e18]
            return whale_txs
        except requests.RequestException as e:
            print(f"خطا در دریافت داده از Arbiscan: {e}")
            return []

    def analyze_token(self, token_id, token_address):
        """تحلیل توکن با ترکیب داده‌های CoinGecko، DexScreener و Arbiscan"""
        prices, volumes = self.get_market_data(token_id)
        if prices.empty or volumes.empty:
            return {"token": token_id, "score": 0, "price": 0, "exit_points": []}

        prices = add_all_ta_features(prices, open="price", high="price", low="price", close="price", volume=volumes["volume"])

        dexscreener_data = self.get_dexscreener_data(token_address)
        volume_score = 20 if dexscreener_data["volume"] > 1e6 else 0
        liquidity_score = 20 if dexscreener_data["liquidity"] > 1e6 else 0

        whale_txs = self.get_whale_transactions(token_address)
        whale_score = len(whale_txs) * 5

        score = 30
        if prices["trend_macd"].iloc[-1] > 0:
            score += 20
        score += volume_score + liquidity_score + min(whale_score, 30)

        return {
            "token": token_id,
            "score": min(score, 100),
            "price": prices["price"].iloc[-1],
            "exit_points": [prices["price"].iloc[-1] * 1.1, prices["price"].iloc[-1] * 0.9]
        }
