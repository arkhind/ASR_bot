#!/bin/bash

echo "🔍 Получаем подробные логи бота..."

echo "📊 Статус сервиса:"
sudo systemctl status asr-bot --no-pager

echo ""
echo "📋 Последние 50 строк логов:"
sudo journalctl -u asr-bot -n 50 --no-pager

echo ""
echo "🐛 Логи с ошибками:"
sudo journalctl -u asr-bot --since "1 hour ago" | grep -i error

echo ""
echo "📝 Все логи за последний час:"
sudo journalctl -u asr-bot --since "1 hour ago" --no-pager
