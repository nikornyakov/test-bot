#!/usr/bin/env python3
"""
Демонстрация годового отчета за 2025 год
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reports.poll_analytics import PollAnalytics, PollResult

def create_realistic_test_data():
    """Создать реалистичные тестовые данные за 2025 год"""
    analytics = PollAnalytics()
    
    # Реальные имена игроков
    players = [
        "Иван Иванов", "Петр Петров", "Сергей Сергеев", "Андрей Андреев",
        "Дмитрий Дмитриев", "Алексей Алексеев", "Михаил Михайлов", "Николай Николаев"
    ]
    
    # Создаем опросы за разные месяцы 2025 года
    test_polls = [
        ("2025-01-15", "15.01.2025", 8, {"✅ Буду": 6, "❌ Не смогу": 1, "🤔 Еще не знаю": 1, "⏰ Планирую опоздать": 0}),
        ("2025-01-22", "22.01.2025", 7, {"✅ Буду": 5, "❌ Не смогу": 2, "🤔 Еще не знаю": 0, "⏰ Планирую опоздать": 0}),
        ("2025-02-05", "05.02.2025", 8, {"✅ Буду": 7, "❌ Не смогу": 1, "🤔 Еще не знаю": 0, "⏰ Планирую опоздать": 0}),
        ("2025-02-19", "19.02.2025", 6, {"✅ Буду": 4, "❌ Не смогу": 1, "🤔 Еще не знаю": 1, "⏰ Планирую опоздать": 0}),
        ("2025-03-12", "12.03.2025", 8, {"✅ Буду": 6, "❌ Не смогу": 1, "🤔 Еще не знаю": 0, "⏰ Планирую опоздать": 1}),
        ("2025-03-26", "26.03.2025", 7, {"✅ Буду": 5, "❌ Не смогу": 1, "🤔 Еще не знаю": 1, "⏰ Планирую опоздать": 0}),
        ("2025-04-09", "09.04.2025", 8, {"✅ Буду": 6, "❌ Не смогу": 2, "🤔 Еще не знаю": 0, "⏰ Планирую опоздать": 0}),
        ("2025-04-23", "23.04.2025", 7, {"✅ Буду": 5, "❌ Не смогу": 1, "🤔 Еще не знаю": 1, "⏰ Планирую опоздать": 0}),
        ("2025-05-07", "07.05.2025", 8, {"✅ Буду": 7, "❌ Не смогу": 1, "🤔 Еще не знаю": 0, "⏰ Планирую опоздать": 0}),
        ("2025-05-21", "21.05.2025", 6, {"✅ Буду": 4, "❌ Не смогу": 1, "🤔 Еще не знаю": 1, "⏰ Планирую опоздать": 0}),
        ("2025-06-04", "04.06.2025", 8, {"✅ Буду": 6, "❌ Не смогу": 1, "🤔 Еще не знаю": 1, "⏰ Планирую опоздать": 0}),
        ("2025-06-18", "18.06.2025", 7, {"✅ Буду": 6, "❌ Не смогу": 1, "🤔 Еще не знаю": 0, "⏰ Планирую опоздать": 0}),
    ]
    
    for i, (date_str, training_date, total_votes, votes) in enumerate(test_polls):
        # Создаем список голосовавших
        voters = []
        vote_count = 0
        for option, count in votes.items():
            for j in range(count):
                voters.append(players[vote_count % len(players)])
                vote_count += 1
        
        # Создаем результат опроса
        poll_result = PollResult(
            poll_id=f"poll_2025_{i}",
            date=date_str,
            question=f"Баскетбол во вторник ({training_date}) 🏀",
            training_date=training_date,
            total_votes=total_votes,
            options=["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Планирую опоздать"],
            votes=votes,
            voters=voters,
            created_at=f"{date_str}T10:00:00"
        )
        
        # Сохраняем
        analytics.save_poll_result(poll_result)
        print(f"✅ Создан опрос от {date_str} - {total_votes} голосов")

def show_yearly_report():
    """Показать полный годовой отчет"""
    print("🏀 ГОДОВОЙ ОТЧЕТ ПО ПОСЕЩАЕМОСТИ - 2025")
    print("=" * 60)
    
    # Создаем тестовые данные
    print("📊 Создание реалистичных тестовых данных...")
    create_realistic_test_data()
    print("✅ Данные созданы\n")
    
    # Создаем аналитику и генерируем отчет
    analytics = PollAnalytics()
    
    print("📈 Генерация годового отчета...")
    report_data = analytics.generate_yearly_report(2025)
    
    # Форматируем и показываем полный отчет
    message = analytics.format_yearly_report_message(report_data)
    
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)
    
    # Дополнительная информация
    print(f"\n📊 Статистика генерации:")
    print(f"• Период: {report_data['period']}")
    print(f"• Всего тренировок: {report_data['total_polls']}")
    print(f"• Среднее участие: {report_data['avg_participation']}")
    print(f"• Месяцев с данными: {len(report_data['monthly_stats'])}")
    print(f"• Игроков в статистике: {len(report_data['player_stats'])}")
    
    print(f"\n🎉 Годовой отчет за 2025 год успешно сформирован!")
    print(f"💡 Для отправки в Telegram установите BOT_TOKEN и GROUP_ID")

if __name__ == "__main__":
    show_yearly_report()
