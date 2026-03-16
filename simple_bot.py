import os
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from bot_base import TelegramBotBase, format_training_date, get_day_of_week

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
        
        # Ищем прогноз на завтра (примерно в 13:00)
        tomorrow_forecast = None
        for item in data['list']:
            # Конвертируем время в timestamp и проверяем завтрашний день в 13:00
            forecast_time = item['dt']
            forecast_dt = datetime.fromtimestamp(forecast_time)
            tomorrow = datetime.now() + timedelta(days=1)
            
            if (forecast_dt.date() == tomorrow.date() and 
                12 <= forecast_dt.hour <= 14):
                tomorrow_forecast = item
                break
        
        if not tomorrow_forecast:
            # Если не нашли точный прогноз, берем первый на завтра
            for item in data['list']:
                forecast_dt = datetime.fromtimestamp(item['dt'])
                tomorrow = datetime.now() + timedelta(days=1)
                if forecast_dt.date() == tomorrow.date():
                    tomorrow_forecast = item
                    break
        
        if not tomorrow_forecast:
            return None
            
        main = tomorrow_forecast['main']
        weather = tomorrow_forecast['weather'][0]
        wind = tomorrow_forecast['wind']
        
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
        training_date = format_training_date(1)
        question = f"Тренировка на улице в воскресенье ({training_date}) в 13:13.\nКто будет?"
        options = ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Опоздаю"]
        poll_message = f"Тренировка на улице в воскресенье ({training_date}) в 13:13. Кто будет?"
        
        # Инициализируем бота
        if not await bot_instance.initialize_bot():
            return False
        
        # Получаем прогноз погоды
        weather_info = get_weather_forecast(training_date)
        
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
Не забудьте:
• Удобную одежду для улицы
• Кроссовки для уличной игры
• Воду
            """
            
            # Добавляем прогноз погоды, если удалось получить
            if weather_info:
                full_message = reminder + f"\n\n{weather_info}"
            else:
                full_message = reminder + "\n\n🌤️ Прогноз погоды временно недоступен"
            
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
