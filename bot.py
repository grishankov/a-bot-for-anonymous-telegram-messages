import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8206796480:AAGlUC2iJtqQ_ijQMcoYfxFrMF51pgOfyk0"

# ID канала, куда будут отправляться анонимные сообщения
# Пример: -1001234567890 (можно получить через @username_to_id_bot или при пересылке сообщения из канала)
CHANNEL_ID = -1001989534408  # Замените на реальный ID вашего канала

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart(deep_link=True))
async def handle_anonymous_message_start(message: Message):
    """
    Обрабатывает deep link вида /start <payload>.
    Ожидается, что бот используется только для приёма анонимных сообщений.
    """
    payload = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    if not payload.startswith("msg_"):
        await message.answer("❌ Неверная ссылка. Используйте корректную ссылку для отправки сообщения.")
        return

    await message.answer(
        "📨 Отправьте ваше анонимное сообщение (текст или фото). "
        "Оно будет отправлено в канал без указания автора."
    )


@dp.message(F.text | F.photo)
async def forward_anonymous_message(message: Message):
    """
    Пересылает любое текстовое сообщение или фото в указанный канал.
    Сообщение отправляется анонимно.
    """
    try:
        if message.photo:
            caption = message.caption or ""
            full_caption = f"📨 <b>Анонимное сообщение:</b>\n\n{caption}" if caption else "📨 <b>Анонимное сообщение</b>"
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=message.photo[-1].file_id,
                caption=full_caption,
                parse_mode="HTML"
            )
        elif message.text:
            text = message.text.strip()
            if not text:
                await message.answer("❌ Текст сообщения не может быть пустым.")
                return
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"📨 <b>Анонимное сообщение:</b>\n\n{text}",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Поддерживаются только текст и фото.")
            return

        await message.answer("✅ Ваше анонимное сообщение успешно отправлено!")

    except Exception as e:
        logger.error(f"Ошибка при отправке в канал: {e}")
        await message.answer(
            "❌ Не удалось отправить сообщение. Пожалуйста, попробуйте позже."
        )


async def main():
    logger.info("Бот запущен. Ожидание анонимных сообщений...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
