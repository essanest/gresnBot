import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from signal_manager import send_signal
from wallet_manager import execute_trade
from config import TELEGRAM_TOKEN, ALLOWED_USER_IDS

def start(update, context):
    if update.message.from_user.id not in ALLOWED_USER_IDS:
        update.message.reply_text("دسترسی غیرمجاز!")
        return
    update.message.reply_text("به essanbot خوش آمدید! دستورات: /signal, /buy, /sell, /mode")

def set_mode(update, context):
    if update.message.from_user.id not in ALLOWED_USER_IDS:
        return
    mode = context.args[0] if context.args else None
    if mode in ["manual", "auto"]:
        context.user_data["mode"] = mode
        update.message.reply_text(f"حالت به {mode} تغییر کرد.")
    else:
        update.message.reply_text("لطفاً حالت valid (manual/auto) را وارد کنید.")

def signal(update, context):
    if update.message.from_user.id not in ALLOWED_USER_IDS:
        return
    signal_data = send_signal()
    update.message.reply_text(
        f"سیگنال: {signal_data['token']}\n"
        f"امتیاز: {signal_data['score']}\n"
        f"اقدام: {signal_data['action']}\n"
        f"قیمت فعلی: {signal_data['price']}\n"
        f"نقاط خروج: {signal_data['exit_points']}"
    )

def buy(update, context):
    if update.message.from_user.id not in ALLOWED_USER_IDS:
        return
    if context.user_data.get("mode") == "manual":
        amount = float(context.args[0]) if context.args else 0
        token = context.args[1] if len(context.args) > 1 else None
        if amount > 0 and token:
            result = execute_trade(token, amount, "buy")
            update.message.reply_text(f"خرید انجام شد: {result}")
        else:
            update.message.reply_text("لطفاً مقدار سرمایه و توکن را مشخص کنید.")
    else:
        update.message.reply_text("حالت دستی فعال نیست!")

def sell(update, context):
    if update.message.from_user.id not in ALLOWED_USER_IDS:
        return
    if context.user_data.get("mode") == "manual":
        amount = float(context.args[0]) if context.args else 0
        token = context.args[1] if len(context.args) > 1 else None
        if amount > 0 and token:
            result = execute_trade(token, amount, "sell")
            update.message.reply_text(f"فروش انجام شد: {result}")
        else:
            update.message.reply_text("لطفاً مقدار توکن و توکن را مشخص کنید.")
    else:
        update.message.reply_text("حالت دستی فعال نیست!")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("mode", set_mode))
    dp.add_handler(CommandHandler("signal", signal))
    dp.add_handler(CommandHandler("buy", buy))
    dp.add_handler(CommandHandler("sell", sell))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
