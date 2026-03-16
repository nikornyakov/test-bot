import os
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from bot_base import TelegramBotBase, format_training_date, get_day_of_week

def get_weather_forecast():
    """Получает прогноз погоды от Яндекс.Погоды для Санкт-Петербурга"""
    try:
        # Яндекс.Погода API (нужен API ключ)
        api_key = os.getenv('YANDEX_WEATHER_API_KEY')
        if not api_key:
            return None
            
        # Координаты Санкт-Петербурга
        lat, lon = 59.9343, 30.3351
        
        url = f"https://api.weather.yandex.ru/v2/forecast"
        headers = {
            'X-Yandex-API-Key': api_key
        }
        params = {
            'lat': lat,
            'lon': lon,
            'limit': 2,  # Сегодня и завтра
            'hours': False
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Получаем прогноз на завтра (для воскресной тренировки)
        tomorrow = data['forecasts'][1]
        
        temp = tomorrow['parts']['day']['temp_avg']
        condition = tomorrow['parts']['day']['condition']
        wind_speed = tomorrow['parts']['day']['wind_speed']
        precipitation = tomorrow['parts']['day']['prec_mm']
        
        # Русские названия условий погоды
        condition_map = {
            'clear': 'ясно',
            'partly-cloudy': 'малооблачно',
            'cloudy': 'облачно с прояснениями',
            'overcast': 'пасмурно',
            'drizzle': 'морось',
            'light-rain': 'небольшой дождь',
            'rain': 'дождь',
            'moderate-rain': 'умеренно сильный дождь',
            'heavy-rain': 'сильный дождь',
            'continuous-heavy-rain': 'проливной дождь',
            'showers': 'ливень',
            'wet-snow': 'мокрый снег',
            'light-snow': 'небольшой снег',
            'snow': 'снег',
            'snow-showers': 'снегопад',
            'hail': 'град',
            'thunderstorm': 'гроза',
            'thunderstorm-with-rain': 'дождь с грозой',
            'thunderstorm-with-hail': 'гроза с градом'
        }
        
        condition_ru = condition_map.get(condition, condition)
        
        weather_info = f"🌤️ *Прогноз на завтра:*\n"
        weather_info += f"🌡️ Температура: {temp}°C\n"
        weather_info += f"☁️ Состояние: {condition_ru}\n"
        weather_info += f"💨 Ветер: {wind_speed} м/с\n"
        
        if precipitation > 0:
            weather_info += f"🌧️ Осадки: {precipitation} мм\n"
            
        # Добавляем рекомендации
        if temp < 5:
            weather_info += "\n🧥 Рекомендация: теплая одежда!"
        elif temp < 15:
            weather_info += "\n 👕 Рекомендация: легкая куртка"
        elif condition in ['rain', 'light-rain', 'moderate-rain', 'heavy-rain']:
            weather_info += "\n☔ Рекомендация: дождевик!"
        else:
            weather_info += "\n☀️ Отличная погода для баскетбола!"
            
        return weather_info
        
    except Exception as e:
        logging.error(f"Ошибка получения прогноза погоды: {e}")
        return None

async def send_welcome_message(bot_instance):
    """Функция отправки приветственного сообщения"""
    welcome_text = """
🏀 *Добро пожаловать в нашу баскетбольную команду!*

Приветствуем тебя в нашем чате! Мы рады видеть нового игрока в нашей дружной компании.

*📅 НАШИ ТРЕНИРОВКИ:*

• **ВТОРНИК**: 19:00-20:30
• **ЧЕТВЕРГ**: 19:00-20:30

*💡 МЕСТО ПРОВЕДЕНИЯ:*
"Basket Hall" 
ул. Салова, 57 корпус 5

*💡 ЧТО НУЖНО ДЛЯ ТРЕНИРОВКИ:*
• Спортивная форма
• Кроссовки (не оставляющие следов на паркете)
• Вода
• Отличное настроение!

Не стесняйся задавать вопросы и активно участвовать в жизни команды. Удачи на площадке! 🏀
        """
    
    success = await bot_instance.send_message(welcome_text, parse_mode='Markdown')
    if success:
        bot_instance.logger.info("Приветственное сообщение отправлено")
    return success

async def send_outdoor_poll():
    """Функция отправки опроса о тренировках на улице с прогнозом погоды"""
    bot_instance = TelegramBotBase("simple_bot.log")
    
    # Определяем текущий день недели
    day_of_week = get_day_of_week()
    
    # Отправляем опрос только в субботу (для воскресной тренировки)
    if day_of_week == 5:  # Суббота
        training_date = format_training_date(1)
        question = f"Баскетбол на улице в воскресенье ({training_date}) 🏀"
        options = ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Опоздаю"]
        poll_message = f"Тренировка на улице в воскресенье ({training_date}) в 13:00. Кто будет?"
        
        # Инициализируем бота
        if not await bot_instance.initialize_bot():
            return False
        
        # Получаем прогноз погоды
        weather_info = get_weather_forecast()
        
        # Отправляем опрос
        success = await bot_instance.send_poll(
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        
        if success:
            # Формируем сообщение с напоминанием и погодой
            reminder = """
            💡 Место проведения: уличная площадка
            Не забудьте:
            • Удобную одежду для улицы
            • Кроссовки для уличной игры
            • Воду
            """
            
            full_message = poll_message + reminder
            
            # Добавляем прогноз погоды, если удалось получить
            if weather_info:
                full_message += f"\n\n{weather_info}"
            else:
                full_message += "\n\n🌤️ Прогноз погоды временно недоступен"
            
            await bot_instance.send_message(full_message)
            bot_instance.logger.info("Опрос о тренировке на улице отправлен с прогнозом погоды")
        
        return success
    else:
        bot_instance.logger.info(f"Сегодня не суббота, опрос о тренировке на улице не требуется")
        return False

async def send_simple_poll():
    """Упрощенная функция отправки опроса"""
    bot_instance = TelegramBotBase("simple_bot.log")
    
    # Определяем текущий день недели
    day_of_week = get_day_of_week()
    
    # Определяем текст опроса в зависимости от дня недели
    if day_of_week == 0:  # Понедельник
        training_date = format_training_date(1)
        question = f"Баскетбол во вторник ({training_date}) 🏀"
        options = ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Планирую опоздать"]
        poll_message = f"Тренировка во вторник ({training_date}) с 19:00 до 20:30. Кто будет?"
        
    elif day_of_week == 2:  # Среда
        training_date = format_training_date(1)
        question = f"Баскетбол в четверг ({training_date}) 🏀"
        options = ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Планирую опоздать"]
        poll_message = f"Тренировка в четверг ({training_date}) с 19:00 до 20:30. Кто будет?"
        
    else:
        bot_instance.logger.info(f"Сегодня не понедельник и не среда, опрос не требуется")
        return False
    
    # Инициализируем бота
    if not await bot_instance.initialize_bot():
        return False
    
    # Отправляем опрос
    success = await bot_instance.send_poll(
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False
    )
    
    if success:
        # Отправляем сообщение с инструкцией
        reminder = """
        💡 Место проведения: Basket Hall 
        по адресу ул. Салова, 57 корпус 5.
        """
        
        await bot_instance.send_message(poll_message + reminder)
        bot_instance.logger.info("Опрос успешно отправлен")
    
    return success

async def send_training_reminder():
    """Функция отправки напоминания о тренировке"""
    bot_instance = TelegramBotBase("simple_bot.log")
    
    # Определяем текущий день недели
    day_of_week = get_day_of_week()
    
    # Отправляем напоминание только по вторникам и четвергам
    if day_of_week == 1:  # Вторник
        training_day = "сегодня"
    elif day_of_week == 3:  # Четверг
        training_day = "сегодня"
    else:
        bot_instance.logger.info(f"Сегодня не вторник и не четверг, напоминание не требуется")
        return False
    
    # Инициализируем бота
    if not await bot_instance.initialize_bot():
        return False
    
    reminder = f"""
⏰ Напоминание
Тренировка {training_day} в 19:00-20:30! 

Не забудьте:
• Спортивную форму
• Кроссовки
• Воду
• Хорошее настроение!

По прибытию на ресепшене узнайте номер зала и раздевалки.
        """
    
    # Отправляем напоминание
    success = await bot_instance.send_message(reminder)
    
    if success:
        bot_instance.logger.info("Напоминание о тренировке отправлено")
    
    return success

async def send_manual_welcome():
    """Функция для ручной отправки приветственного сообщения"""
    bot_instance = TelegramBotBase("simple_bot.log")
    
    if not await bot_instance.initialize_bot():
        return False
    
    success = await send_welcome_message(bot_instance)
    return success

async def main():
    """Основная асинхронная функция"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Запуск упрощенной версии бота")
    logger.info("=" * 50)
    
    # Определяем, что нужно делать в зависимости от дня недели
    day_of_week = get_day_of_week()
    
    # Проверяем, есть ли аргумент командной строки
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "welcome":
            success = await send_manual_welcome()
            if success:
                logger.info("Приветственное сообщение отправлено успешно!")
            else:
                logger.info("Приветственное сообщение не было отправлено")
        elif sys.argv[1] == "outdoor":
            success = await send_outdoor_poll()
            if success:
                logger.info("Опрос о тренировке на улице отправлен успешно!")
            else:
                logger.info("Опрос о тренировке на улице не был отправлен")
    
    elif day_of_week in [0, 2]:  # Понедельник или среда
        success = await send_simple_poll()
        if success:
            logger.info("Опрос отправлен успешно!")
        else:
            logger.info("Опрос не был отправлен")
    
    elif day_of_week in [1, 3]:  # Вторник или четверг
        success = await send_training_reminder()
        if success:
            logger.info("Напоминание отправлено успешно!")
        else:
            logger.info("Напоминание не было отправлено")
    
    else:
        logger.info("Сегодня не день для опросов или напоминаний")
    
    logger.info("Завершение работы")
    logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
