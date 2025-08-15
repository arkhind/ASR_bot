# Руководство по развертыванию ASR Interview Analyzer Bot

## 1. Подготовка сервера

### Выбор сервера
- **VPS/VDS**: DigitalOcean, Linode, Vultr, Hetzner (от $5/месяц)
- **Облачные платформы**: Google Cloud, AWS, Azure
- **Хостинг**: PythonAnywhere, Heroku

### Минимальные требования
- Ubuntu 20.04+ или Debian 11+
- Python 3.8+
- 1GB RAM
- 10GB диска

## 2. Настройка сервера

### Подключение к серверу
```bash
ssh root@your_server_ip
```

### Обновление системы
```bash
apt update && apt upgrade -y
```

### Установка Python и pip
```bash
apt install python3 python3-pip python3-venv -y
```

### Создание пользователя для бота
```bash
adduser botuser
usermod -aG sudo botuser
su - botuser
```

## 3. Загрузка кода

### Клонирование репозитория
```bash
cd /home/botuser
git clone https://github.com/your_username/ASR_bot.git
cd ASR_bot
```

### Или загрузка файлов вручную
```bash
# Создайте файлы main.py, .env, summary_prompt.txt
nano main.py
nano .env
nano summary_prompt.txt
```

## 4. Настройка окружения

### Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
```

### Установка зависимостей
```bash
pip install aiogram telethon requests python-dotenv
```

### Создание файла requirements.txt
```bash
pip freeze > requirements.txt
```

## 5. Настройка .env файла

### Создание .env файла
```bash
nano .env
```

### Содержимое .env
```env
TELEGRAM_BOT_TOKEN=your_bot_token
ELEVENLABS_API_KEY=your_elevenlabs_key
TELETHON_API_ID=your_api_id
TELETHON_API_HASH=your_api_hash
TELETHON_SESSION=your_session_string
OPENROUTER_API_KEY=your_openrouter_key
GROUP_ID=your_group_id
```

## 6. Настройка systemd сервиса

### Создание сервиса
```bash
sudo nano /etc/systemd/system/asr-bot.service
```

### Содержимое сервиса
```ini
[Unit]
Description=ASR Interview Analyzer Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/ASR_bot
Environment=PATH=/home/botuser/ASR_bot/venv/bin
ExecStart=/home/botuser/ASR_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Активация сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable asr-bot
sudo systemctl start asr-bot
```

## 7. Мониторинг и логи

### Проверка статуса
```bash
sudo systemctl status asr-bot
```

### Просмотр логов
```bash
sudo journalctl -u asr-bot -f
```

### Перезапуск бота
```bash
sudo systemctl restart asr-bot
```

## 8. Настройка firewall

### Открытие портов (если нужно)
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 9. Автоматическое обновление

### Создание скрипта обновления
```bash
nano /home/botuser/update_bot.sh
```

### Содержимое скрипта
```bash
#!/bin/bash
cd /home/botuser/ASR_bot
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart asr-bot
```

### Делаем скрипт исполняемым
```bash
chmod +x /home/botuser/update_bot.sh
```

## 10. Резервное копирование

### Создание скрипта бэкапа
```bash
nano /home/botuser/backup_bot.sh
```

### Содержимое скрипта
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /home/botuser/backup_$DATE.tar.gz /home/botuser/ASR_bot
find /home/botuser/backup_*.tar.gz -mtime +7 -delete
```

### Настройка cron для автоматического бэкапа
```bash
crontab -e
# Добавить строку:
0 2 * * * /home/botuser/backup_bot.sh
```

## 11. Troubleshooting

### Частые проблемы

**Бот не запускается:**
```bash
sudo journalctl -u asr-bot -n 50
```

**Проблемы с правами:**
```bash
sudo chown -R botuser:botuser /home/botuser/ASR_bot
```

**Проблемы с зависимостями:**
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Проблемы с .env:**
```bash
# Проверьте права доступа
chmod 600 .env
```

## 12. Мониторинг ресурсов

### Установка htop
```bash
sudo apt install htop -y
htop
```

### Проверка диска
```bash
df -h
```

### Проверка памяти
```bash
free -h
```

## 13. SSL сертификат (опционально)

### Установка Certbot
```bash
sudo apt install certbot -y
```

### Получение сертификата
```bash
sudo certbot certonly --standalone -d your-domain.com
```

## 14. Настройка nginx (опционально)

### Установка nginx
```bash
sudo apt install nginx -y
```

### Настройка конфигурации
```bash
sudo nano /etc/nginx/sites-available/asr-bot
```

### Активация сайта
```bash
sudo ln -s /etc/nginx/sites-available/asr-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
