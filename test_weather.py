#!/usr/bin/env python3
"""Тестовый скрипт для проверки API OpenWeatherMap"""

import os
import sys
sys.path.append('.')

from simple_bot import get_weather_forecast

def test_weather():
    print("🧪 Тестирование API OpenWeatherMap...")
    
    # Установите ваш API ключ
    os.environ['OPENWEATHER_API_KEY'] = 'ваш_api_ключ'
    
    weather = get_weather_forecast()
    
    if weather:
        print("✅ Успешно получен прогноз погоды:")
        print(weather)
    else:
        print("❌ Не удалось получить прогноз погоды")
        print("Проверьте:")
        print("1. Правильность API ключа")
        print("2. Доступность API OpenWeatherMap")
        print("3. Интернет соединение")
        print("4. Активацию API ключа (может потребоваться 2 часа)")

if __name__ == "__main__":
    test_weather()
