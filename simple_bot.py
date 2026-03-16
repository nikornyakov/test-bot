import os
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from bot_base import TelegramBotBase, format_training_date, get_day_of_week

def get_next_sunday_date():
    """Возвращает дату ближайшего воскресенья в формате ДД.ММ.ГГГГ"""
    now = datetime.now()
    current_weekday = now.weekday()  # 0=пн, 6=вс
    
    if current_weekday == 6:  # Сегодня воскресенье
        sunday_date = now
    else:
        # Дней до следующего воскресенья (6 - текущий день недели)
        days_until_sunday = 6 - current_weekday
        sunday_date = now + timedelta(days=days_until_sunday)
    
    return sunday_date.strftime("%d.%m.%Y")

def get_weather_forecast(training_date):
    """Получает прогноз погоды от OpenWeatherMap для Санкт-Петербурга"""
    try:
        # OpenWeatherMap API (нужен API ключ)
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            return None
            
        # Координаты Санкт-Петербурга
        lat, lon = 59.917913, 30.304852
        
        url = f"https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric',  # Цельсий
            'lang': 'ru',    # Русский язык
            'cnt': 8         # Прогноз на 24 часа (3-х часовые интервалы)
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Ищем прогноз на воскресенье (ближайшее)
        target_date = datetime.strptime(training_date, "%d.%m.%Y")
        
        # Ищем прогноз на целевую дату (воскресенье)
        target_forecast = None
        for item in data['list']:
            forecast_dt = datetime.fromtimestamp(item['dt'])
            
            if (forecast_dt.date() == target_date.date() and 
                12 <= forecast_dt.hour <= 14):
                target_forecast = item
                break
        
        if not target_forecast:
            # Если не нашли точный прогноз, берем первый на воскресенье
            for item in data['list']:
                forecast_dt = datetime.fromtimestamp(item['dt'])
                if forecast_dt.date() == target_date.date():
                    target_forecast = item
                    break
        
        if not target_forecast:
            return None
            
        main = target_forecast['main']
        weather = target_forecast['weather'][0]
        wind = target_forecast['wind']
        
        temp = main['temp']
        condition = weather['description']
        wind_speed = wind['speed']
        humidity = main['humidity']
        
        weather_info = f"🌤️ *Прогноз на {training_date}:*\n"
        weather_info += f"🌡️ Температура: {temp:.1f}°C\n"
        weather_info += f"☁️ Состояние: {condition.capitalize()}\n"
        weather_info += f"💨 Ветер: {wind_speed:.1f} м/с\n"
        weather_info += f"💧 Влажность: {humidity}%\n"
        
        # Добавляем рекомендации
        if temp < 5:
            weather_info += "\n🧥 Рекомендация: теплая одежда!"
        elif temp < 15:
            weather_info += "\n👕 Рекомендация: легкая куртка"
        elif 'дождь' in condition.lower() or 'снег' in condition.lower():
            weather_info += "\n☔ Рекомендация: непромокаемая одежда!"
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
    # Временно убираем проверку для тестирования
    # if day_of_week == 5:  # Суббота
    if True:  # Для тестирования - работает каждый день
        # Всегда используем воскресную дату для опроса
        training_date = get_next_sunday_date()
        question = f"🏀 Баскетбол на улице ({training_date}) в 13:13 🏀\nКто будет?"
        options = ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Опоздаю"]
        poll_message = f"Тренировка ({training_date}) в 13:13. Кто будет?"
        
        # Инициализируем бота
        if not await bot_instance.initialize_bot():
            return False
        
        # Получаем прогноз погоды с повторными попытками
        max_retries = 3
        weather_info = None
        
        for attempt in range(max_retries):
            weather_info = get_weather_forecast(training_date)
            if weather_info:
                bot_instance.logger.info(f"Прогноз погоды получен с попытки {attempt + 1}")
                break
            else:
                bot_instance.logger.warning(f"Попытка {attempt + 1}: Прогноз погоды недоступен")
                if attempt < max_retries - 1:
                    bot_instance.logger.info("Повторная попытка через 2 секунды...")
                    import time
                    time.sleep(2)
        
        # Отправляем опрос только если есть прогноз погоды
        if not weather_info:
            bot_instance.logger.error(f"Прогноз погоды недоступен после {max_retries} попыток, опрос не отправлен")
            await bot_instance.send_message("❌ Опрос о тренировке не отправлен: прогноз погоды недоступен")
            return False  # Явно возвращаем код ошибки
        
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
             Адрес: Санкт-Петербург, набережная реки Фонтанки, 130
Ссылка на площадку: https://yandex.ru/maps/-/CPFZZ61k
            """
            
            # Добавляем прогноз погоды (он точно есть, т.к. проверка выше)
            full_message = reminder + f"\n\n{weather_info}"
            
            await bot_instance.send_message(full_message)
            bot_instance.logger.info("Опрос о тренировке на улице отправлен с прогнозом погоды")
        
        return success
    # else:
    #     bot_instance.logger.info(f"Сегодня не суббота, опрос о тренировке на улице не требуется")
    #     return False

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
