#!/bin/bash

# Скрипт для автоматического развертывания ASR Interview Analyzer Bot
# Использование: ./deploy.sh

echo "🚀 Начинаем развертывание ASR Interview Analyzer Bot..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Устанавливаем..."
    sudo apt update
    sudo apt install python3 python3-pip python3-venv -y
fi

# Создаем виртуальное окружение
echo "📦 Создаем виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# Создаем необходимые директории
echo "📁 Создаем директории..."
mkdir -p tmp_files

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте файл .env со следующими переменными:"
    echo "TELEGRAM_BOT_TOKEN=your_bot_token"
    echo "ELEVENLABS_API_KEY=your_elevenlabs_key"
    echo "TELETHON_API_ID=your_api_id"
    echo "TELETHON_API_HASH=your_api_hash"
    echo "TELETHON_SESSION=your_session_string"
    echo "OPENROUTER_API_KEY=your_openrouter_key"
    echo "GROUP_ID=your_group_id"
    exit 1
fi

# Устанавливаем права на .env
chmod 600 .env

# Создаем systemd сервис
echo "🔧 Создаем systemd сервис..."
sudo tee /etc/systemd/system/asr-bot.service > /dev/null <<EOF
[Unit]
Description=ASR Interview Analyzer Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd и запускаем сервис
echo "🚀 Запускаем бота..."
sudo systemctl daemon-reload
sudo systemctl enable asr-bot
sudo systemctl start asr-bot

# Проверяем статус
echo "📊 Проверяем статус бота..."
sleep 3
sudo systemctl status asr-bot --no-pager

echo "✅ Развертывание завершено!"
echo "📋 Полезные команды:"
echo "  Статус бота: sudo systemctl status asr-bot"
echo "  Логи бота: sudo journalctl -u asr-bot -f"
echo "  Перезапуск: sudo systemctl restart asr-bot"
echo "  Остановка: sudo systemctl stop asr-bot"
