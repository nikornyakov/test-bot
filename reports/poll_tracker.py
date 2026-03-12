import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import os
import sys
from telegram import Bot, Poll
from telegram.error import TelegramError

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Для импорта при запуске как модуля
try:
    from .poll_analytics import PollAnalytics, PollResult
except ImportError:
    # Для импорта при запуске как скрипта
    from poll_analytics import PollAnalytics, PollResult

from bot_base import TelegramBotBase


class PollTracker(TelegramBotBase):
    """Класс для отслеживания и сохранения результатов опросов"""
    
    def __init__(self, log_filename="poll_tracker.log"):
        super().__init__(log_filename)
        self.analytics = PollAnalytics()
        
    async def track_poll_results(self, poll_message_id: int) -> bool:
        """Отследить результаты опроса по ID сообщения"""
        try:
            if not self.bot:
                if not await self.initialize_bot():
                    return False
            
            # Получаем информацию об опросе
            poll_info = await self._get_poll_info(poll_message_id)
            if not poll_info:
                self.logger.error(f"Не удалось получить информацию об опросе {poll_message_id}")
                return False
            
            # Сохраняем результат
            poll_result = self._create_poll_result(poll_info)
            success = self.analytics.save_poll_result(poll_result)
            
            if success:
                self.logger.info(f"Результаты опроса {poll_message_id} успешно сохранены")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при отслеживании опроса {poll_message_id}: {e}")
            return False
    
    async def _get_poll_info(self, message_id: int) -> Optional[Dict]:
        """Получить детальную информацию об опросе"""
        try:
            # Получаем сообщение с опросом
            chat = await self.bot.get_chat(self.group_id)
            message = await self.bot.forward_message(
                chat_id=self.group_id,
                from_chat_id=self.group_id,
                message_id=message_id
            )
            
            if message.poll:
                return {
                    'id': message.message_id,
                    'question': message.poll.question,
                    'options': [option.text for option in message.poll.options],
                    'total_voter_count': message.poll.total_voter_count,
                    'options': [
                        {
                            'text': option.text,
                            'voter_count': option.voter_count
                        }
                        for option in message.poll.options
                    ]
                }
            
            return None
            
        except TelegramError as e:
            self.logger.error(f"Ошибка Telegram API при получении опроса: {e}")
            return None
    
    def _create_poll_result(self, poll_info: Dict) -> PollResult:
        """Создать объект PollResult из информации об опросе"""
        # Извлекаем дату тренировки из вопроса
        question = poll_info['question']
        training_date = self._extract_training_date(question)
        
        # Создаем словарь голосов
        votes = {}
        for option in poll_info['options']:
            votes[option['text']] = option['voter_count']
        
        return PollResult(
            poll_id=f"poll_{poll_info['id']}_{datetime.now().strftime('%Y%m%d')}",
            date=datetime.now().strftime('%Y-%m-%d'),
            question=question,
            training_date=training_date,
            total_votes=poll_info['total_voter_count'],
            options=[option['text'] for option in poll_info['options']],
            votes=votes,
            voters=[],  # В реальном приложении здесь были бы ID пользователей
            created_at=datetime.now().isoformat()
        )
    
    def _extract_training_date(self, question: str) -> str:
        """Извлечь дату тренировки из вопроса опроса"""
        import re
        
        # Ищем дату в формате ДД.ММ.ГГГГ
        date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', question)
        if date_match:
            return date_match.group(1)
        
        # Если не нашли, возвращаем текущую дату
        return datetime.now().strftime('%d.%m.%Y')
    
    async def send_monthly_report(self, year: int = None, month: int = None) -> bool:
        """Отправить месячный отчет"""
        try:
            if year is None:
                year = datetime.now().year
            if month is None:
                month = datetime.now().month
            
            # Генерируем отчет
            report_data = self.analytics.generate_monthly_report(year, month)
            
            # Форматируем сообщение
            message = self.analytics.format_report_message(report_data)
            
            # Отправляем в группу
            success = await self.send_message(message, parse_mode='Markdown')
            
            if success:
                self.logger.info(f"Месячный отчет за {year}-{month:02d} отправлен")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке месячного отчета: {e}")
            return False
    
    async def send_attendance_stats(self, days_back: int = 30) -> bool:
        """Отправить статистику посещаемости"""
        try:
            player_stats = self.analytics.calculate_player_stats(days_back)
            
            if not player_stats:
                message = "📊 Нет данных о посещаемости за последние дни"
                return await self.send_message(message)
            
            message = f"📊 *СТАТИСТИКА ПОСЕЩАЕМОСТИ (последние {days_back} дней)*\n\n"
            
            # Топ-5 игроков
            for i, player in enumerate(player_stats[:5], 1):
                message += f"{i}. {player.player_name}: {player.attendance_rate}% "
                message += f"({player.attended}/{player.total_polls})\n"
            
            message += f"\nВсего игроков в статистике: {len(player_stats)}"
            
            success = await self.send_message(message, parse_mode='Markdown')
            
            if success:
                self.logger.info(f"Статистика посещаемости за {days_back} дней отправлена")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке статистики посещаемости: {e}")
            return False


async def test_poll_tracker():
    """Тестирование функциональности PollTracker"""
    tracker = PollTracker()
    
    # Создаем тестовый результат
    from poll_analytics import create_mock_poll_result
    mock_result = create_mock_poll_result()
    
    # Сохраняем результат
    success = tracker.analytics.save_poll_result(mock_result)
    print(f"Тестовый результат сохранен: {success}")
    
    # Генерируем отчет
    if success:
        report = tracker.analytics.generate_monthly_report(2024, 3)
        print("Отчет сгенерирован:")
        print(f"Всего опросов: {report['total_polls']}")
        print(f"Среднее участие: {report['avg_participation']}")
        
        # Отправляем статистику
        await tracker.send_attendance_stats(30)


if __name__ == "__main__":
    asyncio.run(test_poll_tracker())
