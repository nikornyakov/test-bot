import os
import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("get_group_id.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def get_group_id():
    """Функция для получения ID всех групп, где есть бот"""
    try:
        # Получаем токен из переменных окружения
        token = os.getenv("BOT_TOKEN")
        
        # Если токен не найден в переменных окружения, попробуем прочитать из файла .env
        if not token:
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('BOT_TOKEN='):
                            token = line.split('=', 1)[1].strip()
                            break
            except FileNotFoundError:
                pass
        
        if not token:
            logger.error("Не установлен BOT_TOKEN")
            logger.error("Убедитесь, что создали файл .env с BOT_TOKEN=ваш_токен")
            logger.error("Или установите переменную окружения BOT_TOKEN")
            return
        
        # Создаем экземпляр бота
        bot = Bot(token=token)
        logger.info("Бот успешно инициализирован")
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Информация о боте: {bot_info.first_name} (@{bot_info.username})")
        
        # Получаем обновления (сообщения)
        updates = await bot.get_updates()
        
        if not updates:
            logger.info("Не найдено обновлений. Убедитесь, что:")
            logger.info("1. Бот добавлен в группу")
            logger.info("2. В группе отправлено хотя бы одно сообщение")
            return
        
        logger.info("=" * 50)
        logger.info("Найдены следующие чаты/группы:")
        logger.info("=" * 50)
        
        found_groups = False
        
        for update in updates:
            if update.message and update.message.chat:
                chat = update.message.chat
                
                if chat.type in ["group", "supergroup"]:
                    found_groups = True
                    logger.info(f"Группа: {chat.title}")
                    logger.info(f"ID: {chat.id}")
                    logger.info(f"Тип: {chat.type}")
                    logger.info("-" * 30)
        
        if not found_groups:
            logger.info("Группы не найдены. Убедитесь, что:")
            logger.info("1. Бот добавлен в группу как администратор")
            logger.info("2. В группе отправлено хотя бы одно сообщение")
            logger.info("3. Вы используете правильный токен бота")
        
    except TelegramError as e:
        logger.error(f"Ошибка Telegram API: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")

async def main():
    """Основная асинхронная функция"""
    logger.info("=" * 50)
    logger.info("Поиск ID групп для бота")
    logger.info("=" * 50)
    
    await get_group_id()
    
    logger.info("=" * 50)
    logger.info("Завершение работы")
    logger.info("=" * 50)

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main())
