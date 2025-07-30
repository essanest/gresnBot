import os
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ApplicationBuilder
from telegram import Update
from market_analysis import MarketAnalyzer
from wallet_manager import WalletManager
from signal_manager import SignalManager
from dotenv import load_dotenv
from flask import Flask, request
import requests

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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GROK_API_KEY = os.getenv("GROK_API_KEY")

# بررسی وجود متغیرها
if not all([TELEGRAM_TOKEN, TELEGRAM_USER_ID, WEB3_PROVIDER, WALLET_ADDRESS, PRIVATE_KEY, ARBISCAN_API_KEY, COINGECKO_API, DEXSCREENER_API, ARBISCAN_API, WEBHOOK_URL, GROK_API_KEY]):
    raise ValueError("یکی از متغیرهای محیطی ضروری خالی یا تنظیم نشده است!")

# تنظیمات Flask
app = Flask(__name__)

# تنظیمات بات
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# مقداردهی اولیه آسنکرون
async def initialize_app():
    await application.initialize()
    print("Application initialized successfully!")
    asyncio.create_task(monitor_market_continuously())

# تنظیم Webhook
async def set_webhook():
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set successfully!")

# دریافت پاسخ هوشمند از API xAI
def get_smart_response(query):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "grok-3",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 500
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        print(f"خطا در فراخوانی API: {e}")
        return "خطا در پردازش درخواست. لطفاً بعداً امتحان کنید."

# نظارت خودکار بازار
async def monitor_market_continuously():
    while True:
        try:
            analyzer = MarketAnalyzer()
            token_addresses = ["0xaf88d065e77c8cC2239327C5EDb3A432268e5831"]
            for token in token_addresses:
                if analyzer.monitor_market(token):
                    market_data = analyzer.analyze_token("usd-coin", token)
                    if market_data["score"] > 80:
                        await application.bot.send_message(chat_id=TELEGRAM_USER_ID, text=f"سیگنال مطمئن: توکن {token} پتانسیل رشد دارد! قیمت: {market_data['price']}")
        except Exception as e:
            print(f"خطا در نظارت بازار: {e}")
        await asyncio.sleep(300)  # چک هر 5 دقیقه

# تعریف دستورات
async def start(update: Update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        await update.message.reply_text("بات تریدر هوشمند فعال شد! هر سوالی بپرسید یا منتظر سیگنال باشید.")
    else:
        await update.message.reply_text("شما دسترسی ندارید!")

async def signal(update: Update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        analyzer = MarketAnalyzer()
        market_data = analyzer.analyze_token("usd-coin", "0xaf88d065e77c8cC2239327C5EDb3A432268e5831")
        wallet = WalletManager(WEB3_PROVIDER, WALLET_ADDRESS, PRIVATE_KEY)
        signal_mgr = SignalManager(market_data, wallet)
        signal_text = signal_mgr.generate_signal()
        if market_data["score"] > 80:
            await update.message.reply_text(f"سیگنال مطمئن: {signal_text}")
        else:
            await update.message.reply_text(f"تحلیل در حال انجام: {signal_text} (امتیاز: {market_data['score']}/100)")
    else:
        await update.message.reply_text("شما دسترسی ندارید!")

async def handle_message(update: Update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        message_text = update.message.text
        response = get_smart_response(message_text)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("شما دسترسی ندارید!")

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("signal", signal))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# پردازش درخواست‌های وب
@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)
    return 'OK', 200

# route ساده برای تست
@app.route('/', methods=['GET'])
def health_check():
    return 'Service is running', 200

# اجرای برنامه
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(initialize_app())
        loop.run_until_complete(set_webhook())
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
    except KeyboardInterrupt:
        loop.close()
    finally:
        loop.close()
