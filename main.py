import os
import logging
import requests
import re
import json
from datetime import datetime
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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
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

def analyze_interview_with_gemini(text, prompt_file):
    """
    Анализирует текст собеседования с помощью Gemini 2.0 Flash Lite
    """
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY не установлен, анализ пропущен")
        return None
    
    try:
        # Читаем промпт из файла
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Подставляем текст в промпт
        prompt = prompt_template.format(text=text)
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Основные заголовки
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Дополнительные заголовки для ранжирования на OpenRouter
        extra_headers = {
            "HTTP-Referer": "https://github.com/arkhind/ASR_bot",
            "X-Title": "ASR Interview Analyzer"
        }
        
        # Объединяем заголовки
        headers.update(extra_headers)
        
        data = {
            "model": "google/gemini-2.0-flash-lite-001",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            logger.error(f"Ошибка Gemini API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка при анализе с Gemini: {e}")
        return None

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Отправь мне голосовое, видео или аудио сообщение, и я создам краткую сводку собеседования.")

@dp.message(F.content_type.in_({ContentType.VOICE, ContentType.AUDIO, ContentType.VIDEO}))
async def handle_media(message: Message):
    # Только пересылаем в группу, скачивает и транскрибирует Telethon
    await bot.copy_message(
        chat_id=GROUP_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        caption=f"user_id:{message.from_user.id}"
    )

    await message.answer("Файл отправлен на обработку. Создаю сводку собеседования...")

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
            # Создаем сводку с помощью Gemini
            summary = analyze_interview_with_gemini(text, 'summary_prompt.txt')
            
            if summary:
                # Отправляем сводку пользователю
                await bot.send_message(
                    chat_id=user_id,
                    text=f"📋 СВОДКА СОБЕСЕДОВАНИЯ\n\n{summary}"
                )
            else:
                # Если анализ недоступен, отправляем краткую расшифровку
                short_text = text[:1000] + "..." if len(text) > 1000 else text
                await bot.send_message(
                    chat_id=user_id,
                    text=f"📝 РАСШИФРОВКА:\n\n{short_text}\n\n⚠️ Анализ недоступен (установите OPENROUTER_API_KEY)"
                )
            
            # Отправляем краткое сообщение в группу
            short_text = text[:200] + "..." if len(text) > 200 else text
            await bot.send_message(
                chat_id=GROUP_ID, 
                text=f"✅ Обработка завершена для пользователя {user_id}"
            )
            
        else:
            await bot.send_message(chat_id=user_id, text="❌ Не удалось расшифровать файл.")

if __name__ == "__main__":
    import asyncio

    async def main():
        await userbot.start()
        await dp.start_polling(bot)

    asyncio.run(main())
