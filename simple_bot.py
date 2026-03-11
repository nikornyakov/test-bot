import os
import logging
import asyncio
from datetime import datetime, timedelta
from bot_base import TelegramBotBase, format_training_date, get_day_of_week

async def send_welcome_message(bot_instance):
    """Функция отправки приветственного сообщения"""
    welcome_text = """
Привет всем! Ваш бот с баскетбольными пожеланиями! 🏀

*📅 РАСПИСАНИЕ ТРЕНИРОВОК НА СЛЕДУЮЩУЮ НЕДЕЛЮ:*

ВТОРНИК : 🏀 *19:00-20:30*

ЧЕТВЕРГ : 🏀 *19:00-20:30*

*📅 БУДЬТЕ В КУРСЕ:*
Команда Авито играет в турнире Шестового дивизиона НБЛ
🏀 СУББОТА: 29.11 16:10 *Авито vs Балтика*
Смотрите трансляцию https://vk.com/nevabasket

*📍 АДРЕС ЗАЛА:* "Basket Hall" 
ул. Салова, 57 корпус 5

Продуктивных выходных!❄️🏀
        """
    
    success = await bot_instance.send_message(welcome_text, parse_mode='Markdown')
    if success:
        bot_instance.logger.info("Приветственное сообщение отправлено")
    return success

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
    
    # Проверяем, есть ли аргумент командной строки для приветствия
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "welcome":
        success = await send_manual_welcome()
        if success:
            logger.info("Приветственное сообщение отправлено успешно!")
        else:
            logger.info("Приветственное сообщение не было отправлено")
    
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
