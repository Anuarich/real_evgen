import asyncio
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# ═══════════════════════════════════════════════════════
#  НАСТРОЙКИ — заполни один раз
# ═══════════════════════════════════════════════════════
BOT_TOKEN       = '8886457520:AAGHDS5gy6qfWXiT2I9apjxRU_qLP2ZbWbE'
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
PHOTO_URL = 'https://raw.githubusercontent.com/Anuarich/real_evgen/main/evgen2.jpg'

CAPTION = (
    '🏠 *Евгений* — 7 лет занимается арендой квартир в Паттайе, '
    'владелец собственного агентства недвижимости.\n\n'
    'Огромный выбор квартир во всех районах Паттайи!'
)

# Часовой пояс (UTC+7 — Паттайя/Бангкок)
TZ = timezone(timedelta(hours=7))

# ═══════════════════════════════════════════════════════


def notify_text(user, now: str) -> str:
    name = user.full_name or 'Без имени'
    link = f'@{user.username}' if user.username else f'tg://user?id={user.id}'
    return (
        f'🔔 Клиент нажал «Написать Евгению»!\n\n'
        f'👤 {name}\n'
        f'🔗 {link}\n'
        f'📅 {now}\n'
        f'➡️ Переходит к риэлтору'
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    # Кнопка пока что НЕ ведёт по ссылке — сначала шлёт уведомление
    keyboard = [[InlineKeyboardButton(
        '🏠✍️ Написать Евгению', callback_data='go_to_realtor'
    )]]

    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=CAPTION,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def on_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user
    now = datetime.now(TZ).strftime('%d.%m.%Y в %H:%M')

    await query.answer()  # убираем "часики" на кнопке

    # Уведомляем блогера при каждом нажатии кнопки.
    # Пробуем до 3 раз — на случай временного сетевого сбоя.
    for attempt in range(3):
        try:
            await context.bot.send_message(
                chat_id=BLOGGER_CHAT_ID,
                text=notify_text(user, now)
            )
            break
        except Exception as e:
            print(f'Попытка {attempt + 1}: не удалось отправить уведомление блогеру: {e}')
            if attempt < 2:
                await asyncio.sleep(1)

    # Превращаем кнопку в настоящую ссылку — клиенту нужно тапнуть ещё раз
    real_keyboard = [[InlineKeyboardButton(
        '✅ Открыть чат с Евгением', url=REALTOR_LINK
    )]]
    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(real_keyboard)
    )


async def remove_webhook(application: Application) -> None:
    # На случай если ранее был включён webhook — отключаем его,
    # иначе polling будет конфликтовать с ним
    await application.bot.delete_webhook(drop_pending_updates=True)


def main() -> None:
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(remove_webhook)
        .build()
    )
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(on_button_click, pattern='go_to_realtor'))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, start))
    print('Бот запущен ✓')
    app.run_polling()


if __name__ == '__main__':
    main()
