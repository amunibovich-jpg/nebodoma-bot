import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID"))

logging.basicConfig(level=logging.INFO)

NAME, PHONE, ADDRESS = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📐 Записаться на бесплатный замер")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Привет! Добро пожаловать в Небо дома — натяжные потолки под ключ.\n\n"
        "🎁 Мы дарим вам бесплатный замер и расчёт стоимости.\n"
        "⚡ Выезд мастера — в удобное для вас время!\n\n"
        "Нажмите кнопку ниже, чтобы записаться 👇",
        reply_markup=markup
    )

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отлично! 😊 Давайте оформим заявку.\n\nКак вас зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    keyboard = [[KeyboardButton("📱 Отправить мой номер", request_contact=True)]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}! 👋\n\n"
        "Укажите ваш номер телефона:",
        reply_markup=markup
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text
    context.user_data['phone'] = phone
    await update.message.reply_text("📍 Укажите ваш адрес или район города — куда выехать мастеру?")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    name = context.user_data['name']
    phone = context.user_data['phone']
    address = update.message.text
    user = update.message.from_user

    admin_message = (
        "🔔 НОВАЯ ЗАЯВКА — Небо дома\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Телефон: {phone}\n"
        f"📍 Адрес/район: {address}\n"
        f"🆔 Telegram: @{user.username or 'не указан'}\n"
        f"🔗 ID: {user.id}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    keyboard = [[KeyboardButton("📐 Записаться на бесплатный замер")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"✅ Заявка принята, {name}!\n\n"
        "Наш мастер свяжется с вами в течение 30 минут.\n\n"
        "🏠 Небо дома — делаем ваш потолок идеальным!",
        reply_markup=markup
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо, если понадоблюсь — я здесь! 😊")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("📐 Записаться на бесплатный замер"), ask_name)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    print("Бот Небо дома запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
