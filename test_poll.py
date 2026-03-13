import os
import logging
import asyncio
from datetime import datetime
from bot_base import TelegramBotBase, load_token_from_env

async def send_test_poll_async():
    """Асинхронная функция отправки тестового опроса в группу"""
    bot_instance = TelegramBotBase("test_poll.log")
    
    # Инициализируем бота
    if not await bot_instance.initialize_bot():
        return False
    
    # Текст для тестового опроса
    question = f"Баскетбол 24.02, 19:00 - 20:30 🏀"
    options = ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю"]
    message = "Не забудьте взять воду и форму!"
    
    # Отправляем НЕанонимный опрос
    bot_instance.logger.info("Отправляем тестовый опрос в группу")
    success = await bot_instance.send_poll(
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False
    )
    
    if success:
        # Дополнительное текстовое сообщение
        bot_instance.logger.info("Отправляем текстовое сообщение в группу")
        await bot_instance.send_message(message)
        bot_instance.logger.info("Тестовый опрос успешно отправлен")
    
    return success

async def main():
    """Основная асинхронная функция"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Запуск тестового опроса")
    logger.info("=" * 50)
    
    success = await send_test_poll_async()
    
    if success:
        logger.info("Тестирование завершено успешно!")
    else:
        logger.error("Тестирование завершено с ошибками!")
    
    logger.info("Завершение работы")
    logger.info("=" * 50)

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main())
