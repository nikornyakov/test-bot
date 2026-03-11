import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from telegram import Bot
from telegram.error import TelegramError
from bot_base import TelegramBotBase, load_token_from_env, format_training_date, get_day_of_week


class TestTelegramBotBase:
    """Тесты для класса TelegramBotBase"""
    
    def setup_method(self):
        """Настройка тестового окружения"""
        self.bot = TelegramBotBase("test.log")
    
    def test_init(self):
        """Тест инициализации"""
        assert self.bot.log_filename == "test.log"
        assert self.bot.token is None
        assert self.bot.group_id is None
        assert self.bot.bot is None
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': '12345'})
    async def test_get_environment_variables_success(self):
        """Тест успешного получения переменных окружения"""
        result = await self.bot.get_environment_variables()
        assert result is True
        assert self.bot.token == 'test_token'
        assert self.bot.group_id == 12345
    
    @patch.dict(os.environ, {}, clear=True)
    async def test_get_environment_variables_missing(self):
        """Тест отсутствия переменных окружения"""
        result = await self.bot.get_environment_variables()
        assert result is False
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': 'invalid'})
    async def test_get_environment_variables_invalid_group_id(self):
        """Тест невалидного GROUP_ID"""
        result = await self.bot.get_environment_variables()
        assert result is False
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': '12345'})
    @patch('telegram.Bot')
    async def test_initialize_bot_success(self, mock_bot_class):
        """Тест успешной инициализации бота"""
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        result = await self.bot.initialize_bot()
        
        assert result is True
        mock_bot_class.assert_called_once_with(token='test_token')
        assert self.bot.bot == mock_bot
    
    @patch.dict(os.environ, {}, clear=True)
    async def test_initialize_bot_no_token(self):
        """Тест инициализации без токена"""
        result = await self.bot.initialize_bot()
        assert result is False
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': '12345'})
    @patch('telegram.Bot')
    async def test_send_message_success(self, mock_bot_class):
        """Тест успешной отправки сообщения"""
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        await self.bot.initialize_bot()
        
        result = await self.bot.send_message("Test message")
        
        assert result is True
        mock_bot.send_message.assert_called_once_with(
            chat_id=12345,
            text="Test message",
            parse_mode=None
        )
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': '12345'})
    @patch('telegram.Bot')
    async def test_send_message_with_parse_mode(self, mock_bot_class):
        """Тест отправки сообщения с parse_mode"""
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        await self.bot.initialize_bot()
        
        result = await self.bot.send_message("Test message", parse_mode='Markdown')
        
        assert result is True
        mock_bot.send_message.assert_called_once_with(
            chat_id=12345,
            text="Test message",
            parse_mode='Markdown'
        )
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': '12345'})
    @patch('telegram.Bot')
    async def test_send_poll_success(self, mock_bot_class):
        """Тест успешной отправки опроса"""
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        await self.bot.initialize_bot()
        
        result = await self.bot.send_poll(
            question="Test question",
            options=["Option 1", "Option 2"],
            is_anonymous=False,
            allows_multiple_answers=False
        )
        
        assert result is True
        mock_bot.send_poll.assert_called_once_with(
            chat_id=12345,
            question="Test question",
            options=["Option 1", "Option 2"],
            is_anonymous=False,
            allows_multiple_answers=False
        )
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': '12345'})
    @patch('telegram.Bot')
    async def test_send_message_telegram_error(self, mock_bot_class):
        """Тест обработки ошибки Telegram API"""
        mock_bot = AsyncMock()
        mock_bot.send_message.side_effect = TelegramError("API Error")
        mock_bot_class.return_value = mock_bot
        
        await self.bot.initialize_bot()
        
        result = await self.bot.send_message("Test message")
        
        assert result is False
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': '12345'})
    @patch('telegram.Bot')
    async def test_get_bot_info(self, mock_bot_class):
        """Тест получения информации о боте"""
        mock_bot = AsyncMock()
        mock_bot_info = Mock()
        mock_bot_info.first_name = "Test Bot"
        mock_bot_info.username = "testbot"
        mock_bot.get_me.return_value = mock_bot_info
        mock_bot_class.return_value = mock_bot
        
        await self.bot.initialize_bot()
        
        result = await self.bot.get_bot_info()
        
        assert result == mock_bot_info
        mock_bot.get_me.assert_called_once()
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token', 'GROUP_ID': '12345'})
    @patch('telegram.Bot')
    async def test_get_updates(self, mock_bot_class):
        """Тест получения обновлений"""
        mock_bot = AsyncMock()
        mock_updates = [Mock(), Mock()]
        mock_bot.get_updates.return_value = mock_updates
        mock_bot_class.return_value = mock_bot
        
        await self.bot.initialize_bot()
        
        result = await self.bot.get_updates()
        
        assert result == mock_updates
        mock_bot.get_updates.assert_called_once()


class TestUtilityFunctions:
    """Тесты для утилитарных функций"""
    
    def test_load_token_from_env_success(self):
        """Тест успешной загрузки токена из переменных окружения"""
        with patch.dict(os.environ, {'BOT_TOKEN': 'test_token'}):
            token = load_token_from_env()
            assert token == 'test_token'
    
    def test_load_token_from_env_file(self):
        """Тест загрузки токена из файла .env"""
        with patch('builtins.open', mock_open(read_data='BOT_TOKEN=file_token\nOTHER=value')):
            with patch.dict(os.environ, {}, clear=True):
                token = load_token_from_env()
                assert token == 'file_token'
    
    def test_load_token_from_env_missing(self):
        """Тест отсутствия токена"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with patch.dict(os.environ, {}, clear=True):
                token = load_token_from_env()
                assert token is None
    
    def test_format_training_date(self):
        """Тест форматирования даты тренировки"""
        from datetime import datetime, timedelta
        
        # Мокаем текущую дату
        with patch('bot_base.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.strftime.return_value = "01.01.2024"
            mock_datetime.now.return_value = mock_now
            
            # Мокаем timedelta
            with patch('bot_base.timedelta') as mock_timedelta:
                mock_timedelta.return_value = timedelta(days=1)
                
                date = format_training_date(1)
                assert date == "01.01.2024"
    
    def test_get_day_of_week(self):
        """Тест получения дня недели"""
        with patch('bot_base.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.weekday.return_value = 2  # Среда
            mock_datetime.now.return_value = mock_now
            
            day = get_day_of_week()
            assert day == 2


def mock_open(read_data=""):
    """Хелпер для мокания open"""
    from unittest.mock import mock_open as _mock_open
    return _mock_open(read_data=read_data)
