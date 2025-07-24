import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import requests

# Логирование
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Папка для временных файлов
TMP_DIR = 'tmp_files'
os.makedirs(TMP_DIR, exist_ok=True)

async def transcribe_with_elevenlabs(file_path: str) -> str:
    url = 'https://api.elevenlabs.io/v1/speech-to-text'
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
    }
    files = {
        'file': open(file_path, 'rb'),  # исправлено с 'audio' на 'file'
    }
    data = {
        'model_id': 'scribe_v1',
        'language': 'auto',
        'task': 'transcribe',
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        result = response.json()
        return result.get('text', 'Текст не распознан.')
    else:
        return f'Ошибка распознавания: {response.text}'

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer('Привет! Пришли мне аудио или видео файл (mp3, mp4 и др.), и я распознаю текст с помощью ElevenLabs.')

@dp.message(F.document | F.audio | F.video | F.voice)
async def handle_media(message: Message):
    file = None
    file_name = None
    if message.document:
        file = message.document
        file_name = file.file_name
    elif message.audio:
        file = message.audio
        file_name = file.file_name or f"audio_{file.file_id}.mp3"
    elif message.video:
        file = message.video
        file_name = file.file_name or f"video_{file.file_id}.mp4"
    elif message.voice:
        file = message.voice
        file_name = f"voice_{file.file_id}.ogg"
    else:
        await message.reply('Пожалуйста, отправьте аудио или видео файл.')
        return

    file_path = os.path.join(TMP_DIR, file_name)
    await bot.download(file, destination=file_path)
    await message.reply('Файл получен, начинаю распознавание...')
    try:
        text = await transcribe_with_elevenlabs(file_path)
        await message.reply(f'Распознанный текст:\n{text}')
    except Exception as e:
        await message.reply(f'Ошибка при распознавании: {e}')
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))
