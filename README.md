# ASR Interview Analyzer Bot

🤖 Telegram бот для анализа собеседований с помощью AI

## Описание

Этот бот автоматически:
- Расшифровывает аудио/видео файлы с помощью ElevenLabs
- Анализирует текст собеседования с помощью Gemini AI
- Создает структурированную сводку интервью

## Возможности

✅ **Поддержка больших файлов** (до 2GB)  
✅ **Множество форматов**: mp3, mp4, wav, avi, mov, mkv  
✅ **AI анализ**: извлечение ключевых моментов, навыков, вопросов  
✅ **Автоматический перезапуск** при сбоях  
✅ **Подробное логирование**  

## Быстрая установка

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/your_username/ASR_bot.git
cd ASR_bot
```

### 2. Создайте .env файл
```bash
cp .env.example .env
nano .env
```

### 3. Запустите автоматическое развертывание
```bash
./deploy.sh
```

## Настройка .env файла

```env
TELEGRAM_BOT_TOKEN=your_bot_token
ELEVENLABS_API_KEY=your_elevenlabs_key
TELETHON_API_ID=your_api_id
TELETHON_API_HASH=your_api_hash
TELETHON_SESSION=your_session_string
OPENROUTER_API_KEY=your_openrouter_key
GROUP_ID=your_group_id
```

## Получение API ключей

### Telegram Bot Token
1. Напишите @BotFather в Telegram
2. Создайте нового бота: `/newbot`
3. Скопируйте полученный токен

### ElevenLabs API Key
1. Зарегистрируйтесь на [elevenlabs.io](https://elevenlabs.io)
2. Перейдите в Settings → API Key
3. Скопируйте ключ

### Telethon API
1. Зайдите на [my.telegram.org](https://my.telegram.org)
2. Войдите в аккаунт
3. Создайте приложение
4. Скопируйте API ID и API Hash

### OpenRouter API Key
1. Зарегистрируйтесь на [openrouter.ai](https://openrouter.ai)
2. Перейдите в API Keys
3. Создайте новый ключ

## Управление ботом

```bash
# Статус
sudo systemctl status asr-bot

# Логи
sudo journalctl -u asr-bot -f

# Перезапуск
sudo systemctl restart asr-bot

# Остановка
sudo systemctl stop asr-bot
```

## Структура проекта

```
ASR_bot/
├── main.py              # Основной код бота
├── .env                 # Конфигурация (не в git)
├── summary_prompt.txt   # Промпт для анализа
├── requirements.txt     # Python зависимости
├── deploy.sh           # Скрипт развертывания
├── deployment_guide.md # Подробное руководство
└── README.md           # Этот файл
```

## Архитектура

- **aiogram** - основной Telegram бот
- **Telethon** - userbot для больших файлов
- **ElevenLabs** - распознавание речи
- **OpenRouter + Gemini** - анализ текста

## Поддерживаемые форматы

### Аудио
- mp3, wav, ogg, m4a, flac

### Видео  
- mp4, avi, mov, mkv, wmv

### Telegram
- Голосовые сообщения
- Аудио/видео файлы

## Ограничения

- Максимальный размер файла: 2GB
- Время обработки зависит от длительности
- Требует стабильное интернет-соединение

## Troubleshooting

### Бот не запускается
```bash
sudo journalctl -u asr-bot -n 50
```

### Проблемы с правами
```bash
sudo chown -R $USER:$USER /path/to/bot
chmod 600 .env
```

### Проблемы с зависимостями
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Лицензия

MIT License

## Поддержка

Если у вас есть вопросы или проблемы, создайте Issue в репозитории.
