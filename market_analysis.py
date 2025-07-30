import os
import requests
import pandas as pd
from ta import add_all_ta_features
from dotenv import load_dotenv
import json
import time

# بارگذاری متغیرهای محیطی
load_dotenv()

class MarketAnalyzer:
    def __init__(self):
        self.COINGECKO_API = os.getenv("COINGECKO_API")
        self.DEXSCREENER_API = os.getenv("DEXSCREENER_API")
        self.ARBISCAN_API = os.getenv("ARBISCAN_API")
        self.ARBISCAN_API_KEY = os.getenv("ARBISCAN_API_KEY")

    def get_market_data(self, token_id="bitcoin"):
        url = f"{self.COINGECKO_API}/coins/{token_id}/market_chart?vs_currency=usd&days=1"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
            prices["high"] = prices["price"]
            prices["low"] = prices["price"]
            prices["open"] = prices["price"].shift(1).fillna(prices["price"])
            prices["close"] = prices["price"]
            min_length = min(len(prices), len(volumes))
            prices = prices.iloc[:min_length].reset_index(drop=True)
            volumes = volumes.iloc[:min_length].reset_index(drop=True)
            if not all(col in prices.columns for col in ["open", "high", "low", "close"]):
                raise ValueError("DataFrame lacks required columns for TA analysis")
            return prices, volumes
        except requests.RequestException as e:
            print(f"خطا در دریافت داده از CoinGecko: {e}")
            return pd.DataFrame(columns=["timestamp", "price", "high", "low", "open", "close"]), pd.DataFrame(columns=["timestamp", "volume"])

    def get_dexscreener_data(self, token_address):
        url = f"{self.DEXSCREENER_API}/tokens/{token_address}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            volume = data.get("volume", {}).get("h24", 0)
            liquidity = data.get("liquidity", {}).get("usd", 0)
            return {"volume": volume, "liquidity": liquidity}
        except requests.RequestException as e:
            print(f"خطا در دریافت داده از DexScreener: {e}")
            return {"volume": 0, "liquidity": 0"}

    def get_whale_transactions(self, token_address):
        url = f"{self.ARBISCAN_API}?module=account&action=tokentx&contractaddress={token_address}&sort=desc&apikey={self.ARBISCAN_API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            transactions = data.get("result", [])
            whale_txs = []
            for tx in transactions:
                try:
                    if isinstance(tx, dict):
                        value = float(tx.get("value", 0))
                    elif isinstance(tx, str):
                        tx_data = json.loads(tx)
                        value = float(tx_data.get("value", 0))
                    else:
                        continue
                    if value > 1e18:
                        whale_txs.append(tx)
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
            return whale_txs
        except requests.RequestException as e:
            print(f"خطا در دریافت داده از Arbiscan: {e}")
            return []

    def monitor_market(self, token_address):
        dexscreener_data = self.get_dexscreener_data(token_address)
        volume = dexscreener_data["volume"]
        liquidity = dexscreener_data["liquidity"]
        whale_txs = self.get_whale_transactions(token_address)
        if volume > 1e6 and liquidity > 1e6 and len(whale_txs) > 5:
            return True
        return False

    def analyze_token(self, token_id, token_address):
        prices, volumes = self.get_market_data(token_id)
        if prices.empty or volumes.empty:
            return {"token": token_id, "score": 0, "price": 0, "exit_points": []}

        try:
            prices = add_all_ta_features(
                prices,
                open="open",
                high="high",
                low="low",
                close="close",
                volume=volumes["volume"].values,
                fillna=True
            )
        except KeyError as e:
            print(f"KeyError in add_all_ta_features: {e}")
            prices["trend_macd"] = 0

        dexscreener_data = self.get_dexscreener_data(token_address)
        volume_score = 20 if dexscreener_data["volume"] > 1e6 else 0
        liquidity_score = 20 if dexscreener_data["liquidity"] > 1e6 else 0

        whale_txs = self.get_whale_transactions(token_address)
        whale_score = min(len(whale_txs) * 5, 30)

        score = 30
        if prices["trend_macd"].iloc[-1] > 0:
            score += 20
        score += volume_score + liquidity_score + whale_score

        return {
            "token": token_id,
            "score": min(score, 100),
            "price": prices["price"].iloc[-1] if not prices.empty else 0,
            "exit_points": [prices["price"].iloc[-1] * 1.1, prices["price"].iloc[-1] * 0.9] if not prices.empty else []
        }
