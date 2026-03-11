import os
import logging
import asyncio
from bot_base import TelegramBotBase, load_token_from_env

async def get_group_id():
    """Функция для получения ID всех групп, где есть бот"""
    bot_instance = TelegramBotBase("get_group_id.log")
    
    # Получаем токен с дополнительной проверкой из файла .env
    token = load_token_from_env()
    if not token:
        bot_instance.logger.error("Не установлен BOT_TOKEN")
        bot_instance.logger.error("Убедитесь, что создали файл .env с BOT_TOKEN=ваш_токен")
        bot_instance.logger.error("Или установите переменную окружения BOT_TOKEN")
        return
    
    # Устанавливаем токен напрямую
    bot_instance.token = token
    
    # Инициализируем бота
    if not await bot_instance.initialize_bot():
        return
    
    # Получаем информацию о боте
    bot_info = await bot_instance.get_bot_info()
    if bot_info:
        bot_instance.logger.info(f"Информация о боте: {bot_info.first_name} (@{bot_info.username})")
    
    # Получаем обновления (сообщения)
    updates = await bot_instance.get_updates()
    
    if not updates:
        bot_instance.logger.info("Не найдено обновлений. Убедитесь, что:")
        bot_instance.logger.info("1. Бот добавлен в группу")
        bot_instance.logger.info("2. В группе отправлено хотя бы одно сообщение")
        return
    
    bot_instance.logger.info("=" * 50)
    bot_instance.logger.info("Найдены следующие чаты/группы:")
    bot_instance.logger.info("=" * 50)
    
    found_groups = False
    
    for update in updates:
        if update.message and update.message.chat:
            chat = update.message.chat
            
            if chat.type in ["group", "supergroup"]:
                found_groups = True
                bot_instance.logger.info(f"Группа: {chat.title}")
                bot_instance.logger.info(f"ID: {chat.id}")
                bot_instance.logger.info(f"Тип: {chat.type}")
                bot_instance.logger.info("-" * 30)
    
    if not found_groups:
        bot_instance.logger.info("Группы не найдены. Убедитесь, что:")
        bot_instance.logger.info("1. Бот добавлен в группу как администратор")
        bot_instance.logger.info("2. В группе отправлено хотя бы одно сообщение")
        bot_instance.logger.info("3. Вы используете правильный токен бота")

async def main():
    """Основная асинхронная функция"""
    logger = logging.getLogger(__name__)
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
