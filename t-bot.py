import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def send_poll_async():
    """Асинхронная функция отправки опроса в группу"""
    try:
        # Получаем токен из переменных окружения
        token = os.getenv("BOT_TOKEN")
        group_id = os.getenv("GROUP_ID")
        
        logger.info(f"Получены переменные: BOT_TOKEN={token[:10]}..., GROUP_ID={group_id}")
        
        if not token or not group_id:
            logger.error("Не установлены BOT_TOKEN или GROUP_ID")
            return False
        
        # Преобразуем group_id в целое число
        try:
            group_id = int(group_id)
        except ValueError:
            logger.error(f"GROUP_ID должен быть числом, получено: {group_id}")
            return False
        
        # Определяем текущий день недели
        now = datetime.now()
        day_of_week = now.weekday()  # 0-пн, 1-вт, 2-ср, 3-чт, 4-пт, 5-сб, 6-вс
        day_name = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"][day_of_week]
        
        logger.info(f"Текущий день: {day_name} ({day_of_week})")
        
        # Форматируем дату для отображения
        date_str = now.strftime("%d.%m.%Y")
        
        # Определяем текст опроса в зависимости от дня недели
        if day_of_week == 0:  # Понедельник
            # Опрос создается в понедельник для тренировки во вторник
            training_date = (now + timedelta(days=1)).strftime("%d.%m.%Y")
            question = f"Баскетбол во вторник ({training_date}) 🏀"
            options = ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю"]
            message = f"Тренировка во вторник ({training_date}) с 19:00 до 20:30. Кто будет?"
            
        elif day_of_week == 2:  # Среда
            # Опрос создается в среду для тренировки в четверг
            training_date = (now + timedelta(days=1)).strftime("%d.%m.%Y")
            question = f"Баскетбол в четверг ({training_date}) 🏀"
            options = ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю"]
            message = f"Тренировка в четверг ({training_date}) с 19:00 до 20:30. Кто будет?"
            
        else:
            logger.info(f"Сегодня {day_name}, опрос не требуется")
            return False
        
        # Создаем экземпляр бота
        bot = Bot(token=token)
        logger.info("Бот успешно инициализирован")
        
        # Отправляем НЕанонимный опрос (асинхронно)
        logger.info(f"Отправляем опрос в группу: {question}")
        await bot.send_poll(
            chat_id=group_id,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        
        # Дополнительное текстовое сообщение (асинхронно)
        logger.info("Отправляем текстовое сообщение в группу")
        await bot.send_message(
            chat_id=group_id,
            text=message
        )
        
        logger.info("Опрос успешно отправлен")
        return True
        
    except TelegramError as e:
        logger.error(f"Ошибка Telegram API при отправке опроса: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке опроса: {e}")
        return False

async def main():
    """Основная асинхронная функция"""
    logger.info("=" * 50)
    logger.info("Запуск бота для отправки опроса")
    logger.info("=" * 50)
    
    success = await send_poll_async()
    
    if success:
        logger.info("Опрос отправлен успешно!")
    else:
        logger.info("Опрос не был отправлен (не подходящий день или ошибка)")
    
    logger.info("Завершение работы")
    logger.info("=" * 50)

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main())
