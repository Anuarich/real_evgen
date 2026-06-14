from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ═══════════════════════════════════════════════════════
#  НАСТРОЙКИ — заполни один раз
# ═══════════════════════════════════════════════════════
BOT_TOKEN       = '8886457520:AAGtOfaBMZAF_xmeI-teG0Y2y-0Sngn1wHE'
BLOGGER_CHAT_ID = '241473802'

# Ссылка на риэлтора с заготовленным сообщением
REALTOR_LINK = (
    'https://t.me/John007001?text='
    '%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5'
    '%2C%20%D1%83%D0%B2%D0%B8%D0%B4%D0%B5%D0%BB%20%D0%B2%D0%B0%D1%81%20%D0%BD'
    '%D0%B0%20%D0%BA%D0%B0%D0%BD%D0%B0%D0%BB%D0%B5%20%D0%95%D0%BB%D0%B5%D0%BD'
    '%D1%8B%20%D0%B8%20%D0%90%D0%BD%D0%B2%D0%B0%D1%80%D0%B0%2C%20%D0%B8%D0%BD'
    '%D1%82%D0%B5%D1%80%D0%B5%D1%81%D1%83%D0%B5%D1%82%20%D0%BA%D0%B2%D0%B0%D1'
    '%80%D1%82%D0%B8%D1%80%D0%B0%20%D0%B2%20%D0%9F%D0%B0%D1%82%D1%82%D0%B0%D0'
    '%B9%D0%B5.'
)

# Фото и текст для клиента
PHOTO_URL = 'https://raw.githubusercontent.com/Anuarich/real_evgen/main/evgen.jpg'

CAPTION = (
    '🏠 *Евгений* — 7 лет занимается арендой квартир в Паттайе, '
    'владелец собственного агентства недвижимости.\n\n'
    'Огромный выбор квартир во всех районах Паттайи!'
)

# Часовой пояс (UTC+7 — Паттайя/Бангкок)
TZ = timezone(timedelta(hours=7))

# ═══════════════════════════════════════════════════════

# Запоминаем уже уведомлённых клиентов (сбрасывается при перезапуске)
notified: set[int] = set()


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    now  = datetime.now(TZ).strftime('%d.%m.%Y в %H:%M')
    name = user.full_name or 'Без имени'
    link = f'@{user.username}' if user.username else f'tg://user?id={user.id}'

    # Уведомляем блогера только при первом обращении клиента
    if user.id not in notified:
        notified.add(user.id)
        await context.bot.send_message(
            chat_id=BLOGGER_CHAT_ID,
            text=(
                f'🔔 *Новый клиент!*\n\n'
                f'👤 {name}\n'
                f'🔗 {link}\n'
                f'📅 {now}\n'
                f'➡️ Перенаправлен к риэлтору'
            ),
            parse_mode='Markdown'
        )

    # Отвечаем клиенту: фото + текст + кнопка
    keyboard = [[InlineKeyboardButton('✉️ Написать Евгению', url=REALTOR_LINK)]]
    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=CAPTION,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', handle))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle))
    print('Бот запущен ✓')
    app.run_polling()


if __name__ == '__main__':
    main()
