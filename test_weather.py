#!/usr/bin/env python3
"""Тестовый скрипт для проверки API Яндекс.Погоды"""

import os
import sys
sys.path.append('.')

from simple_bot import get_weather_forecast

def test_weather():
    print("🧪 Тестирование API Яндекс.Погоды...")
    
    # Установите ваш API ключ
    os.environ['YANDEX_WEATHER_API_KEY'] = 'ваш_api_ключ'
    
    weather = get_weather_forecast()
    
    if weather:
        print("✅ Успешно получен прогноз погоды:")
        print(weather)
    else:
        print("❌ Не удалось получить прогноз погоды")
        print("Проверьте:")
        print("1. Правильность API ключа")
        print("2. Доступность API Яндекс.Погоды")
        print("3. Интернет соединение")

if __name__ == "__main__":
    test_weather()
