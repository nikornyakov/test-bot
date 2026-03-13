import json
import os
from typing import Dict, Any, List


class Config:
    """Класс для работы с конфигурацией бота"""
    
    def __init__(self, config_file: str = "config.json"):
        """Инициализация конфигурации"""
        self.config_file = config_file
        self._config = None
        self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации из файла"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл конфигурации {self.config_file} не найден")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON в файле {self.config_file}: {e}")
    
    def get(self, key_path: str, default=None):
        """Получение значения по пути вида 'section.subsection.key'"""
        if not self._config:
            return default
        
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_schedule(self) -> Dict[str, Any]:
        """Получение конфигурации расписания"""
        return self.get('schedule', {})
    
    def get_venue(self) -> Dict[str, str]:
        """Получение информации о месте проведения"""
        return self.get('venue', {})
    
    def get_messages(self) -> Dict[str, Any]:
        """Получение шаблонов сообщений"""
        return self.get('messages', {})
    
    def get_team_info(self) -> Dict[str, str]:
        """Получение информации о команде"""
        return self.get('team', {})
    
    def get_logging_config(self) -> Dict[str, str]:
        """Получение конфигурации логирования"""
        return self.get('logging', {})
    
    def get_training_days(self) -> List[int]:
        """Получение дней тренировок"""
        return self.get('schedule.training_days', [1, 3])
    
    def get_poll_days(self) -> List[int]:
        """Получение дней для опросов"""
        return self.get('schedule.poll_days', [0, 2])
    
    def get_training_time(self) -> str:
        """Получение времени тренировок"""
        return self.get('schedule.training_time', '19:00-20:30')
    
    def get_venue_name(self) -> str:
        """Получение названия зала"""
        return self.get('venue.name', 'Basket Hall')
    
    def get_venue_address(self) -> str:
        """Получение адреса зала"""
        return self.get('venue.address', 'ул. Салова, 57 корпус 5')
    
    def get_welcome_message(self) -> str:
        """Формирование приветственного сообщения"""
        messages = self.get_messages()
        welcome = messages.get('welcome', {})
        
        return f"""
{welcome.get('title', 'Привет всем! Ваш бот с баскетбольными пожеланиями! 🏀')}

{welcome.get('schedule_title', '📅 РАСПИСАНИЕ ТРЕНИРОВОК НА СЛЕДУЮЩУЮ НЕДЕЛЮ:')}

{welcome.get('tuesday', 'ВТОРНИК : 🏀 *19:00-20:30*')}

{welcome.get('thursday', 'ЧЕТВЕРГ : 🏀 *19:00-20:30*')}

{welcome.get('news_title', '📅 БУДЬТЕ В КУРСЕ:')}
{welcome.get('team_news', 'Команда Авито играет в турнире Шестового дивизиона НБЛ')}
{welcome.get('match_info', '🏀 СУБТОТА: 29.11 16:10 *Авито vs Балтика*')}
{welcome.get('stream_link', 'Смотрите трансляцию https://vk.com/nevabasket')}

{welcome.get('venue_title', '📍 АДРЕС ЗАЛА:')}
{welcome.get('venue_info', '"Basket Hall" \nул. Салова, 57 корпус 5')}

{welcome.get('closing', 'Продуктивных выходных!❄️🏀')}
        """
    
    def get_poll_question(self, day: int, date: str) -> str:
        """Получение вопроса для опроса"""
        messages = self.get_messages()
        poll = messages.get('poll', {})
        
        if day == 0:  # Понедельник -> вторник
            template = poll.get('tuesday_template', 'Баскетбол во вторник ({date}) 🏀')
        elif day == 2:  # Среда -> четверг
            template = poll.get('thursday_template', 'Баскетбол в четверг ({date}) 🏀')
        else:
            template = 'Баскетбол ({date}) 🏀'
        
        return template.format(date=date)
    
    def get_poll_message(self, day: int, date: str) -> str:
        """Получение сообщения для опроса"""
        messages = self.get_messages()
        poll = messages.get('poll', {})
        
        if day == 0:  # Понедельник -> вторник
            template = poll.get('tuesday_message', 'Тренировка во вторник ({date}) с 19:00 до 20:30. Кто будет?')
        elif day == 2:  # Среда -> четверг
            template = poll.get('thursday_message', 'Тренировка в четверг ({date}) с 19:00 до 20:30. Кто будет?')
        else:
            template = 'Тренировка ({date}) с 19:00 до 20:30. Кто будет?'
        
        return template.format(date=date)
    
    def get_poll_options(self) -> List[str]:
        """Получение вариантов ответа для опроса"""
        return self.get('messages.poll.options', ['✅ Буду', '❌ Не смогу', '🤔 Еще не знаю', '⏰ Планирую опоздать'])
    
    def get_venue_reminder(self) -> str:
        """Получение напоминания о месте проведения"""
        return self.get('messages.poll.venue_reminder', '💡 Место проведения: Basket Hall \nпо адресу ул. Салова, 57 корпус 5.')
    
    def get_reminder_message(self, day: str) -> str:
        """Получение сообщения напоминания"""
        messages = self.get_messages()
        reminder = messages.get('reminder', {})
        
        message = reminder.get('message_template', 'Тренировка {day} в 19:00-20:30!').format(day=day)
        
        dont_forget = reminder.get('dont_forget', 'Не забудьте:')
        items = '\n'.join(reminder.get('items', ['• Спортивную форму', '• Кроссовки', '• Воду', '• Хорошее настроение!']))
        reception_info = reminder.get('reception_info', 'По прибытию на ресепшене узнайте номер зала и раздевалки.')
        
        return f"""
{reminder.get('title', '⏰ Напоминание')}
{message}

{dont_forget}
{items}

{reception_info}
        """
    
    def get_test_poll_question(self, date: str) -> str:
        """Получение вопроса для тестового опроса"""
        template = self.get('messages.test.question_template', 'Баскетбол {date}, 19:00 - 20:30 🏀')
        return template.format(date=date)
    
    def get_test_poll_options(self) -> List[str]:
        """Получение вариантов ответа для тестового опроса"""
        return self.get('messages.test.options', ['✅ Буду', '❌ Не смогу', '🤔 Еще не знаю'])
    
    def get_test_message(self) -> str:
        """Получение тестового сообщения"""
        return self.get('messages.test.message', 'Не забудьте взять воду и форму!')
    
    def reload(self):
        """Перезагрузка конфигурации"""
        self.load_config()


# Глобальный экземпляр конфигурации
config = Config()
