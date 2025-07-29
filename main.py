import os
from telegram.ext import Application, CommandHandler
from market_analysis import MarketAnalyzer
from wallet_manager import WalletManager
from signal_manager import SignalManager
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# دریافت متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ARBISCAN_API_KEY = os.getenv("ARBISCAN_API_KEY")
COINGECKO_API = os.getenv("COINGECKO_API")
DEXSCREENER_API = os.getenv("DEXSCREENER_API")
ARBISCAN_API = os.getenv("ARBISCAN_API")

# بررسی وجود متغیرها
if not all([TELEGRAM_TOKEN, TELEGRAM_USER_ID, WEB3_PROVIDER, WALLET_ADDRESS, PRIVATE_KEY, ARBISCAN_API_KEY, COINGECKO_API, DEXSCREENER_API, ARBISCAN_API]):
    raise ValueError("یکی از متغیرهای محیطی ضروری خالی یا تنظیم نشده است!")

# تنظیمات بات
application = Application.builder().token(TELEGRAM_TOKEN).build()

# تعریف دستورات
async def start(update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        await update.message.reply_text("بات فعال شد! از /signal برای تحلیل استفاده کنید.")
    else:
        await update.message.reply_text("شما دسترسی ندارید!")

async def signal(update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        # فراخوانی MarketAnalyzer با توکن نمونه
        analyzer = MarketAnalyzer()
        market_data = analyzer.analyze_token("bitcoin", "0x1234...")  # جایگزین با آدرس واقعی
        wallet = WalletManager(WEB3_PROVIDER, WALLET_ADDRESS, PRIVATE_KEY)
        signal_mgr = SignalManager(market_data, wallet)
        await update.message.reply_text(signal_mgr.generate_signal())
    else:
        await update.message.reply_text("شما دسترسی ندارید!")

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("signal", signal))

# اجرای بات
print("بات در حال اجرا است...")
application.run_polling(allowed_updates=[])
