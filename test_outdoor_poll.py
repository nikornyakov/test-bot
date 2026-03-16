#!/usr/bin/env python3
"""Тестовый скрипт для проверки опроса о тренировках на улице"""

import os
import sys
import asyncio
sys.path.append('.')

from simple_bot import send_outdoor_poll

async def test_outdoor_poll():
    print("🧪 Тестирование опроса о тренировках на улице...")
    
    # Установите переменные окружения
    os.environ['YANDEX_WEATHER_API_KEY'] = 'ваш_api_ключ'
    os.environ['BOT_TOKEN'] = 'ваш_токен_бота'
    os.environ['GROUP_ID'] = 'id_чата'
    
    # Запускаем тест
    success = await send_outdoor_poll()
    
    if success:
        print("✅ Опрос успешно отправлен!")
    else:
        print("❌ Не удалось отправить опрос")
        print("Проверьте:")
        print("1. Правильность токена бота")
        print("2. ID чата")
        print("3. Добавлен ли бот в чат")

if __name__ == "__main__":
    asyncio.run(test_outdoor_poll())
