import os
import logging
import requests
import re
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
MODEL_ID = "scribe_v1"
GROUP_ID = int(os.getenv("GROUP_ID"))

TELETHON_API_ID = int(os.getenv("TELETHON_API_ID"))
TELETHON_API_HASH = os.getenv("TELETHON_API_HASH")
TELETHON_SESSION = os.getenv("TELETHON_SESSION")

# Вход в аккаунт через Telethon
userbot = TelegramClient(StringSession(TELETHON_SESSION), TELETHON_API_ID, TELETHON_API_HASH)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

def transcribe(file_path):
    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    with open(file_path, "rb") as f:
        files = {
            "file": (os.path.basename(file_path), f, "audio/ogg"),
        }
        data = {
            "model_id": MODEL_ID,
            "language": "auto"
        }

        response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        logger.error(f"Ошибка от ElevenLabs: {response.status_code} {response.text}")
        return None

    return response.json().get("text", "[Пусто]")

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Отправь мне голосовое, видео или аудио сообщение, и я его расшифрую.")

@dp.message(F.content_type.in_({ContentType.VOICE, ContentType.AUDIO, ContentType.VIDEO}))
async def handle_media(message: Message):
    # Только пересылаем в группу, скачивает и транскрибирует Telethon
    await bot.copy_message(
        chat_id=GROUP_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        caption=f"user_id:{message.from_user.id}"
    )

    await message.answer("Файл отправлен на транскрипцию. Ожидайте...")

# Слушать сообщения в группе и скачивать их
@userbot.on(events.NewMessage(chats=GROUP_ID))
async def download_from_group(event):
    if event.voice or event.audio or event.video:
        media = await event.download_media()
        logger.info(f"Telethon: скачан файл {media}")

        # Извлекаем user_id из текста (caption)
        match = re.search(r"user_id:(\d+)", event.message.message or "")
        user_id = int(match.group(1)) if match else None

        if not media or not user_id:
            logger.warning("Нет файла или user_id для транскрипции")
            return

        text = transcribe(media)

        os.remove(media)
        logger.info("Файл удалён после транскрипции")

        if text:
            # Отправить в группу и пользователю
            await bot.send_message(chat_id=GROUP_ID, text=f"📝 Расшифровка:\n{text}")
            await bot.send_message(chat_id=user_id, text=f"📝 Расшифровка:\n{text}")
        else:
            await bot.send_message(chat_id=user_id, text="❌ Не удалось расшифровать файл.")

if __name__ == "__main__":
    import asyncio

    async def main():
        await userbot.start()
        await dp.start_polling(bot)

    asyncio.run(main())
