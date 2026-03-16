import pytest
import asyncio
import tempfile
import json
import os
from unittest.mock import patch, AsyncMock, Mock
from simple_bot import send_welcome_message, send_simple_poll, send_training_reminder

pytestmark = pytest.mark.asyncio


class TestSimpleBot:
    """Тесты для основных функций simple_bot.py"""
    
    def setup_method(self):
        """Настройка тестового окружения"""
        # Создаем временный конфигурационный файл
        self.test_config = {
            "schedule": {
                "training_days": [1, 3],
                "poll_days": [0, 2],
                "training_time": "19:00-20:30"
            },
            "venue": {
                "name": "Basket Hall",
                "address": "ул. Салова, 57 корпус 5"
            },
            "messages": {
                "welcome": {
                    "title": "Привет всем! Ваш бот с баскетбольными пожеланиями! 🏀",
                    "schedule_title": "📅 РАСПИСАНИЕ ТРЕНИРОВОК НА СЛЕДУЮЩУЮ НЕДЕЛЮ:",
                    "tuesday": "ВТОРНИК : 🏀 *19:00-20:30*",
                    "thursday": "ЧЕТВЕРГ : 🏀 *19:00-20:30*",
                    "news_title": "📅 БУДЬТЕ В КУРСЕ:",
                    "team_news": "Команда Авито играет в турнире Шестового дивизиона НБЛ",
                    "match_info": "🏀 СУББОТА: 29.11 16:10 *Авито vs Балтика*",
                    "stream_link": "Смотрите трансляцию https://vk.com/nevabasket",
                    "venue_title": "📍 АДРЕС ЗАЛА:",
                    "venue_info": '"Basket Hall" \nул. Салова, 57 корпус 5',
                    "closing": "Продуктивных выходных!❄️🏀"
                },
                "poll": {
                    "tuesday_template": "Баскетбол во вторник ({date}) 🏀",
                    "thursday_template": "Баскетбол в четверг ({date}) 🏀",
                    "tuesday_message": "Тренировка во вторник ({date}) с 19:00 до 20:30. Кто будет?",
                    "thursday_message": "Тренировка в четверг ({date}) с 19:00 до 20:30. Кто будет?",
                    "options": ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Планирую опоздать"],
                    "venue_reminder": "💡 Место проведения: Basket Hall \nпо адресу ул. Салова, 57 корпус 5."
                },
                "reminder": {
                    "title": "⏰ Напоминание",
                    "message_template": "Тренировка {day} в 19:00-20:30!",
                    "dont_forget": "Не забудьте:",
                    "items": [
                        "• Спортивную форму",
                        "• Кроссовки",
                        "• Воду",
                        "• Хорошее настроение!"
                    ],
                    "reception_info": "По прибытию на ресепшене узнайте номер зала и раздевалки."
                }
            },
            "team": {
                "name": "Авито",
                "league": "НБЛ",
                "division": "Шестовой дивизион"
            }
        }
        
        # Создаем временный файл конфигурации
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_file)
        self.temp_file.close()
    
    def teardown_method(self):
        """Очистка тестового окружения"""
        os.unlink(self.temp_file.name)
    
    @patch('simple_bot.TelegramBotBase')
    async def test_send_welcome_message_success(self, mock_bot_base_class):
        """Тест успешной отправки приветственного сообщения"""
        mock_bot = AsyncMock()
        mock_bot.send_message.return_value = True
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_welcome_message(mock_bot)
        
        assert result is True
        mock_bot.send_message.assert_called_once()
        
        # Проверяем, что сообщение содержит ожидаемые элементы из нового приветствия
        call_args = mock_bot.send_message.call_args
        # call_args это tuple (positional_args, keyword_args)
        positional_args, keyword_args = call_args
        # В функции send_message используется positional аргумент для текста
        message_text = positional_args[0]  # Первый позиционный аргумент - текст
        assert keyword_args['parse_mode'] == 'Markdown'
        assert 'Добро пожаловать в нашу баскетбольную команду!' in message_text
        assert 'НАШИ ТРЕНИРОВКИ:' in message_text
        assert '**ВТОРНИК**: 19:00-20:30' in message_text
        assert '**ЧЕТВЕРГ**: 19:00-20:30' in message_text
        assert 'Basket Hall' in message_text
        assert 'ул. Салова, 57 корпус 5' in message_text
        assert 'Спортивная форма' in message_text
        assert 'Кроссовки (не оставляющие следов на паркете)' in message_text
        assert 'Вода' in message_text
        assert 'Отличное настроение!' in message_text
    
    @patch('simple_bot.TelegramBotBase')
    @patch('simple_bot.get_day_of_week')
    async def test_send_simple_poll_monday(self, mock_get_day, mock_bot_base_class):
        """Тест отправки опроса в понедельник"""
        mock_get_day.return_value = 0  # Понедельник
        mock_bot = AsyncMock()
        mock_bot.initialize_bot.return_value = True
        mock_bot.send_poll.return_value = True
        mock_bot.send_message.return_value = True
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_simple_poll()
        
        assert result is True
        mock_bot.initialize_bot.assert_called_once()
        mock_bot.send_poll.assert_called_once()
        mock_bot.send_message.assert_called_once()
        
        # Проверяем параметры опроса
        poll_call = mock_bot.send_poll.call_args[1]
        assert 'вторник' in poll_call['question']
        assert poll_call['is_anonymous'] is False
        assert poll_call['allows_multiple_answers'] is False
        assert len(poll_call['options']) == 4
    
    @patch('simple_bot.TelegramBotBase')
    @patch('simple_bot.get_day_of_week')
    async def test_send_simple_poll_wednesday(self, mock_get_day, mock_bot_base_class):
        """Тест отправки опроса в среду"""
        mock_get_day.return_value = 2  # Среда
        mock_bot = AsyncMock()
        mock_bot.initialize_bot.return_value = True
        mock_bot.send_poll.return_value = True
        mock_bot.send_message.return_value = True
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_simple_poll()
        
        assert result is True
        poll_call = mock_bot.send_poll.call_args[1]
        assert 'четверг' in poll_call['question']
    
    @patch('simple_bot.TelegramBotBase')
    @patch('simple_bot.get_day_of_week')
    async def test_send_simple_poll_wrong_day(self, mock_get_day, mock_bot_base_class):
        """Тест отправки опроса в неправильный день"""
        mock_get_day.return_value = 1  # Вторник
        mock_bot = AsyncMock()
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_simple_poll()
        
        assert result is False
        mock_bot.initialize_bot.assert_not_called()
        mock_bot.send_poll.assert_not_called()
    
    @patch('simple_bot.TelegramBotBase')
    @patch('simple_bot.get_day_of_week')
    async def test_send_training_reminder_tuesday(self, mock_get_day, mock_bot_base_class):
        """Тест отправки напоминания во вторник"""
        mock_get_day.return_value = 1  # Вторник
        mock_bot = AsyncMock()
        mock_bot.initialize_bot.return_value = True
        mock_bot.send_message.return_value = True
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_training_reminder()
        
        assert result is True
        mock_bot.initialize_bot.assert_called_once()
        mock_bot.send_message.assert_called_once()
        
        # Проверяем содержание сообщения
        call_args = mock_bot.send_message.call_args
        positional_args, keyword_args = call_args
        message_text = positional_args[0]  # Первый позиционный аргумент - текст
        assert 'сегодня' in message_text
        assert 'Тренировка' in message_text
        assert 'Спортивную форму' in message_text
    
    @patch('simple_bot.TelegramBotBase')
    @patch('simple_bot.get_day_of_week')
    async def test_send_training_reminder_thursday(self, mock_get_day, mock_bot_base_class):
        """Тест отправки напоминания в четверг"""
        mock_get_day.return_value = 3  # Четверг
        mock_bot = AsyncMock()
        mock_bot.initialize_bot.return_value = True
        mock_bot.send_message.return_value = True
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_training_reminder()
        
        assert result is True
        mock_bot.initialize_bot.assert_called_once()
        mock_bot.send_message.assert_called_once()
        
        # Проверяем содержание сообщения
        call_args = mock_bot.send_message.call_args
        positional_args, keyword_args = call_args
        message_text = positional_args[0]  # Первый позиционный аргумент - текст
        assert 'сегодня' in message_text
    
    @patch('simple_bot.TelegramBotBase')
    @patch('simple_bot.get_day_of_week')
    async def test_send_training_reminder_wrong_day(self, mock_get_day, mock_bot_base_class):
        """Тест отправки напоминания в неправильный день"""
        mock_get_day.return_value = 0  # Понедельник
        mock_bot = AsyncMock()
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_training_reminder()
        
        assert result is False
        mock_bot.initialize_bot.assert_not_called()
        mock_bot.send_message.assert_not_called()
    
    @patch('simple_bot.TelegramBotBase')
    @patch('simple_bot.get_day_of_week')
    async def test_send_simple_poll_initialization_failure(self, mock_get_day, mock_bot_base_class):
        """Тест обработки ошибки инициализации бота при отправке опроса"""
        mock_get_day.return_value = 0  # Понедельник
        mock_bot = AsyncMock()
        mock_bot.initialize_bot.return_value = False
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_simple_poll()
        
        assert result is False
        mock_bot.send_poll.assert_not_called()
        mock_bot.send_message.assert_not_called()
    
    @patch('simple_bot.TelegramBotBase')
    @patch('simple_bot.get_day_of_week')
    async def test_send_training_reminder_initialization_failure(self, mock_get_day, mock_bot_base_class):
        """Тест обработки ошибки инициализации бота при отправке напоминания"""
        mock_get_day.return_value = 1  # Вторник
        mock_bot = AsyncMock()
        mock_bot.initialize_bot.return_value = False
        mock_bot_base_class.return_value = mock_bot
        
        result = await send_training_reminder()
        
        assert result is False
        mock_bot.send_message.assert_not_called()
