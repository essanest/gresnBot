import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from telegram.ext import Application, CommandHandler
from config import TELEGRAM_TOKEN, TELEGRAM_USER_ID
from market_analysis import analyze_market
from wallet_manager import WalletManager
from signal_manager import SignalManager
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیمات بات
application = Application.builder().token(TELEGRAM_TOKEN).build()

# تعریف دستورات
def start(update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        update.message.reply_text("بات فعال شد! از /signal برای تحلیل استفاده کنید.")
    else:
        update.message.reply_text("شما دسترسی ندارید!")

def signal(update, context):
    if str(update.effective_user.id) == TELEGRAM_USER_ID:
        market_data = analyze_market()
        wallet = WalletManager()
        signal = SignalManager(market_data, wallet)
        update.message.reply_text(signal.generate_signal())
    else:
        update.message.reply_text("شما دسترسی ندارید!")

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("signal", signal))

# تابع برای اجرای سرور HTTP ساده (برای راضی کردن Render)
def run_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()

# اجرای سرور در یک ترد جداگانه
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

# اجرای بات
print("بات در حال اجرا است...")
application.run_polling()
