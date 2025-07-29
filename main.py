import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ApplicationBuilder
from telegram import Update
from market_analysis import MarketAnalyzer
from wallet_manager import WalletManager
from signal_manager import SignalManager
from dotenv import load_dotenv
from flask import Flask, request

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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # باید تو .env تنظیم بشه (مثلاً https://your-render-url.onrender.com)

# بررسی وجود متغیرها
if not all([TELEGRAM_TOKEN, TELEGRAM_USER_ID, WEB3_PROVIDER, WALLET_ADDRESS, PRIVATE_KEY, ARBISCAN_API_KEY, COINGECKO_API, DEXSCREENER_API, ARBISCAN_API, WEBHOOK_URL]):
    raise ValueError("یکی از متغیرهای محیطی ضروری خالی یا تنظیم نشده است!")

# تنظیمات Flask
app = Flask(__name__)

# تنظیمات بات
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# تعریف دستورات
async def start(update: Update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        await update.message.reply_text("بات تریدر هوشمند فعال شد! از /signal برای سیگنال استفاده کنید یا سوال بپرسید.")
    else:
        await update.message.reply_text("شما دسترسی ندارید!")

async def signal(update: Update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        analyzer = MarketAnalyzer()
        market_data = analyzer.analyze_token("usd-coin", "0xaf88d065e77c8cC2239327C5EDb3A432268e5831")
        wallet = WalletManager(WEB3_PROVIDER, WALLET_ADDRESS, PRIVATE_KEY)
        signal_mgr = SignalManager(market_data, wallet)
        await update.message.reply_text(signal_mgr.generate_signal())
    else:
        await update.message.reply_text("شما دسترسی ندارید!")

async def handle_message(update: Update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        message_text = update.message.text.lower()
        if "قیمت" in message_text:
            analyzer = MarketAnalyzer()
            market_data = analyzer.analyze_token("usd-coin", "0xaf88d065e77c8cC2239327C5EDb3A432268e5831")
            await update.message.reply_text(f"قیمت فعلی USDC: {market_data['price']}")
        else:
            await update.message.reply_text(f"پیام شما: {update.message.text}. برای سیگنال /signal رو امتحان کن!")
    else:
        await update.message.reply_text("شما دسترسی ندارید!")

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("signal", signal))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# تنظیم Webhook
async def set_webhook():
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set successfully!")

# پردازش درخواست‌های وب
@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)
    return 'OK'

# اجرای برنامه
if __name__ == '__main__':
    import asyncio
    asyncio.run(set_webhook())
    app.run(host='0.0.0.0', port=8080)
