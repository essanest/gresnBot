import os
from dotenv import load_dotenv

load_dotenv()

# تنظیمات تلگرام
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# تنظیمات APIهای بازار
COINGECKO_API = "https://api.coingecko.com/api/v3"  # API رایگان
DEXSCREENER_API = "https://api.dexscreener.com/latest/v1"  # API برای ردیابی توکن‌ها
ARBISCAN_API = "https://api.arbiscan.io/api"  # API برای تراکنش‌های Arbitrum
ARBISCAN_API_KEY = os.getenv("ARBISCAN_API_KEY")  # کلید API Arbiscan

# تنظیمات بلاک‌چین
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")  # مثلاً https://arbitrum-one-rpc.publicnode.com
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")  # مثلاً 0xD15fBdba08e12C865c37751F57D3F936d56fd2d8
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # کلید خصوصی (در محیط امن ذخیره شود)

# تنظیمات بات
ALLOWED_USER_IDS = [int(os.getenv("TELEGRAM_USER_ID"))]  # آیدی تلگرام کاربران مجاز
