#!/usr/bin/env python3
"""
Простой сборщик опросов из Telegram группы
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Добавляем директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot_base import TelegramBotBase

class SimplePollCollector(TelegramBotBase):
    """Простой сборщик опросов"""
    
    def __init__(self):
        super().__init__()
        self.polls_file = Path('reports/polls.json')
        self.users_file = Path('reports/users.json')
        
    def load_existing_data(self) -> dict:
        """Загрузить существующие данные"""
        try:
            if self.polls_file.exists():
                with open(self.polls_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных: {e}")
            return {}
    
    def save_data(self, data: dict):
        """Сохранить данные"""
        try:
            self.polls_file.parent.mkdir(exist_ok=True)
            with open(self.polls_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Данные сохранены: {len(data)} опросов")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения данных: {e}")
    
    def extract_poll_info(self, update) -> dict:
        """Извлечь информацию об опросе из обновления"""
        try:
            if not hasattr(update, 'message') or not update.message:
                return None
                
            message = update.message
            if not hasattr(message, 'poll') or not message.poll:
                return None
            
            poll = message.poll
            poll_id = str(poll.id)
            
            # Извлекаем дату тренировки из вопроса
            training_date = self._extract_training_date(poll.question)
            
            # Собираем данные о вариантах ответов
            options = []
            votes = {}
            
            for option in poll.options:
                option_text = option.text
                option_votes = option.voter_count
                options.append(option_text)
                votes[option_text] = option_votes
            
            poll_data = {
                'poll_id': poll_id,
                'date': message.date.strftime('%Y-%m-%d'),
                'question': poll.question,
                'training_date': training_date,
                'total_votes': poll.total_voter_count,
                'options': options,
                'votes': votes,
                'message_id': message.message_id,
                'created_at': message.date.isoformat()
            }
            
            return poll_data
            
        except Exception as e:
            self.logger.error(f"Ошибка извлечения данных опроса: {e}")
            return None
    
    def _extract_training_date(self, question: str) -> str:
        """Извлечь дату тренировки из вопроса"""
        import re
        
        # Ищем дату в формате ДД.ММ.ГГГГ
        date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', question)
        if date_match:
            return date_match.group(1)
        
        # Ищем дату в формате ДД.ММ
        date_match = re.search(r'(\d{2}\.\d{2})', question)
        if date_match:
            return date_match.group(1) + f".{datetime.now().year}"
        
        # Если не нашли, возвращаем текущую дату
        return datetime.now().strftime('%d.%m.%Y')
    
    async def collect_recent_polls(self, limit: int = 50) -> int:
        """Собрать последние опросы из обновлений"""
        try:
            self.logger.info("Начинаем сбор опросов из обновлений...")
            
            # Получаем обновления
            updates = await self.get_updates()
            
            if not updates:
                self.logger.warning("Обновления не получены")
                return 0
            
            # Загружаем существующие данные
            existing_data = self.load_existing_data()
            collected_count = 0
            
            # Обрабатываем обновления
            for update in updates:
                poll_info = self.extract_poll_info(update)
                if poll_info:
                    poll_id = poll_info['poll_id']
                    
                    # Если опрос еще не сохранен, добавляем его
                    if poll_id not in existing_data:
                        existing_data[poll_id] = poll_info
                        collected_count += 1
                        self.logger.info(f"Добавлен опрос: {poll_info['question']}")
            
            # Сохраняем данные
            if collected_count > 0:
                self.save_data(existing_data)
                self.logger.info(f"Собрано новых опросов: {collected_count}")
            else:
                self.logger.info("Новых опросов не найдено")
            
            return collected_count
            
        except Exception as e:
            self.logger.error(f"Ошибка сбора опросов: {e}")
            return 0
    
    async def listen_for_polls(self, duration: int = 60):
        """Слушать новые опросы в реальном времени"""
        try:
            self.logger.info(f"Начинаем прослушивание на {duration} секунд...")
            
            start_time = datetime.now()
            collected_count = 0
            existing_data = self.load_existing_data()
            
            while (datetime.now() - start_time).seconds < duration:
                try:
                    # Получаем обновления
                    updates = await self.get_updates()
                    
                    for update in updates:
                        poll_info = self.extract_poll_info(update)
                        if poll_info:
                            poll_id = poll_info['poll_id']
                            
                            if poll_id not in existing_data:
                                existing_data[poll_id] = poll_info
                                collected_count += 1
                                self.logger.info(f"Новый опрос: {poll_info['question']}")
                                
                                # Сохраняем каждый новый опрос
                                self.save_data(existing_data)
                    
                    # Ждем перед следующим запросом
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    self.logger.error(f"Ошибка в цикле прослушивания: {e}")
                    await asyncio.sleep(5)
            
            self.logger.info(f"Прослушивание завершено. Собрано опросов: {collected_count}")
            return collected_count
            
        except Exception as e:
            self.logger.error(f"Ошибка прослушивания: {e}")
            return 0

async def main():
    """Основная функция"""
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 ПРОСТОЙ СБОРЩИК ОПРОСОВ")
    print("=" * 40)
    
    collector = SimplePollCollector()
    
    # Инициализируем бота
    if not await collector.initialize_bot():
        print("❌ Не удалось инициализировать бота")
        return
    
    print("✅ Бот инициализирован")
    
    # Собираем последние опросы
    collected = await collector.collect_recent_polls()
    print(f"📊 Собрано опросов: {collected}")
    
    # Опционально: слушаем новые опросы
    if collected > 0:
        print("\n🎉 Данные успешно собраны!")
        print("Теперь можно генерировать отчеты:")
        print("python3 reports/generate_reports.py yearly 2025")
    else:
        print("\n💡 Опросы не найдены.")
        print("Возможные решения:")
        print("1. Убедитесь, что бот добавлен в группу")
        print("2. Отправьте /start в группе")
        print("3. Создайте новый опрос в группе")
        print("4. Проверьте GROUP_ID в .env файле")

if __name__ == "__main__":
    asyncio.run(main())
