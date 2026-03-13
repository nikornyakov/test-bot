import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError


class TelegramBotBase:
    """Базовый класс для Telegram ботов с общей функциональностью"""
    
    def __init__(self, log_filename="bot.log"):
        """Инициализация базового класса"""
        self.setup_logging(log_filename)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.token = None
        self.group_id = None
        self.bot = None
    
    def setup_logging(self, log_filename):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    async def get_environment_variables(self):
        """Получение и валидация переменных окружения"""
        self.token = os.getenv("BOT_TOKEN")
        self.group_id = os.getenv("GROUP_ID")
        
        # Логируем токен безопасно
        if self.token:
            self.logger.info(f"Получены переменные: BOT_TOKEN={self.token[:10]}..., GROUP_ID={self.group_id}")
        else:
            self.logger.info(f"Получены переменные: BOT_TOKEN=None, GROUP_ID={self.group_id}")
        
        if not self.token or not self.group_id:
            self.logger.error("Не установлены BOT_TOKEN или GROUP_ID")
            return False
        
        # Преобразуем group_id в целое число
        try:
            self.group_id = int(self.group_id)
        except ValueError:
            self.logger.error(f"GROUP_ID должен быть числом, получено: {self.group_id}")
            return False
        
        return True
    
    async def initialize_bot(self):
        """Инициализация бота"""
        if not self.token:
            if not await self.get_environment_variables():
                return False
        
        try:
            self.bot = Bot(token=self.token)
            self.logger.info("Бот успешно инициализирован")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации бота: {e}")
            return False
    
    async def send_message(self, text, parse_mode=None):
        """Отправка текстового сообщения"""
        if not self.bot:
            if not await self.initialize_bot():
                return False
        
        try:
            await self.bot.send_message(
                chat_id=self.group_id,
                text=text,
                parse_mode=parse_mode
            )
            self.logger.info("Сообщение успешно отправлено")
            return True
        except TelegramError as e:
            self.logger.error(f"Ошибка Telegram API при отправке сообщения: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при отправке сообщения: {e}")
            return False
    
    async def send_poll(self, question, options, is_anonymous=False, allows_multiple_answers=False):
        """Отправка опроса"""
        if not self.bot:
            if not await self.initialize_bot():
                return False
        
        try:
            await self.bot.send_poll(
                chat_id=self.group_id,
                question=question,
                options=options,
                is_anonymous=is_anonymous,
                allows_multiple_answers=allows_multiple_answers
            )
            self.logger.info(f"Опрос успешно отправлен: {question}")
            return True
        except TelegramError as e:
            self.logger.error(f"Ошибка Telegram API при отправке опроса: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при отправке опроса: {e}")
            return False
    
    async def get_bot_info(self):
        """Получение информации о боте"""
        if not self.bot:
            if not await self.initialize_bot():
                return None
        
        try:
            return await self.bot.get_me()
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о боте: {e}")
            return None
    
    async def get_updates(self):
        """Получение обновлений"""
        if not self.bot:
            if not await self.initialize_bot():
                return []
        
        try:
            return await self.bot.get_updates()
        except Exception as e:
            self.logger.error(f"Ошибка при получении обновлений: {e}")
            return []


def load_token_from_env():
    """Загрузка токена из файла .env если он не найден в переменных окружения"""
    token = os.getenv("BOT_TOKEN")
    
    if not token:
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('BOT_TOKEN='):
                        token = line.split('=', 1)[1].strip()
                        break
        except FileNotFoundError:
            pass
    
    return token


def format_training_date(date_offset_days=1):
    """Форматирование даты для тренировки"""
    now = datetime.now()
    training_date = (now + timedelta(days=date_offset_days)).strftime("%d.%m.%Y")
    return training_date


def get_day_of_week():
    """Получение текущего дня недели (0=пн, 1=вт, ...)"""
    return datetime.now().weekday()
