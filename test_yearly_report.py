#!/usr/bin/env python3
"""
Тестовый скрипт для проверки годового отчета
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reports.poll_analytics import PollAnalytics, create_mock_poll_result

def create_test_data_for_2025():
    """Создать тестовые данные за 2025 год"""
    analytics = PollAnalytics()
    
    # Создаем тестовые опросы за разные месяцы 2025 года
    test_dates = [
        '2025-01-15', '2025-01-22', '2025-02-05', '2025-02-19',
        '2025-03-12', '2025-03-26', '2025-04-09', '2025-04-23',
        '2025-05-07', '2025-05-21', '2025-06-04', '2025-06-18'
    ]
    
    players = ['Игрок1', 'Игрок2', 'Игрок3', 'Игрок4', 'Игрок5', 'Игрок6', 'Игрок7', 'Игрок8']
    
    for i, date_str in enumerate(test_dates):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Создаем тестовый результат
        mock_result = create_mock_poll_result()
        
        # Обновляем дату и ID
        mock_result.date = date_str
        mock_result.training_date = date_obj.strftime('%d.%m.%Y')
        mock_result.poll_id = f"test_poll_2025_{i}"
        mock_result.created_at = date_obj.isoformat()
        
        # Варьируем количество голосов и результаты
        mock_result.total_votes = 6 + (i % 3)
        mock_result.votes = {
            "✅ Буду": 4 + (i % 2),
            "❌ Не смогу": 1,
            "🤔 Еще не знаю": 1 if i % 3 == 0 else 0,
            "⏰ Планирую опоздать": 1 if i % 4 == 0 else 0
        }
        
        # Создаем список голосовавших
        voters = []
        for j in range(mock_result.total_votes):
            voters.append(f"user{j+1}")
        mock_result.voters = voters
        
        # Сохраняем
        analytics.save_poll_result(mock_result)
        print(f"Создан тестовый опрос от {date_str} - {mock_result.total_votes} голосов")

def test_yearly_report():
    """Тестирование годового отчета"""
    print("🧪 Тестирование годового отчета за 2025 год")
    print("=" * 50)
    
    # Создаем тестовые данные
    print("📊 Создание тестовых данных...")
    create_test_data_for_2025()
    print("✅ Тестовые данные созданы\n")
    
    # Создаем аналитику
    analytics = PollAnalytics()
    
    # Генерируем годовой отчет
    print("📈 Генерация годового отчета...")
    try:
        report_data = analytics.generate_yearly_report(2025)
        
        print(f"📅 Период: {report_data['period']}")
        print(f"🏀 Всего тренировок: {report_data['total_polls']}")
        print(f"👥 Среднее участие: {report_data['avg_participation']}")
        print(f"📊 Месяцев с данными: {len(report_data['monthly_stats'])}")
        print(f"🏆 Игроков в статистике: {len(report_data['player_stats'])}")
        
        # Показываем помесячную статистику
        print("\n📈 Помесячная статистика:")
        for month_data in report_data['monthly_stats'].values():
            emoji = "🔥" if month_data['avg_participation'] >= 6 else "👍" if month_data['avg_participation'] >= 4 else "📊"
            print(f"  {month_data['month_name']}: {month_data['polls']} тренировок, {month_data['avg_participation']} в среднем {emoji}")
        
        # Показываем топ-3 игроков
        print("\n🏆 Топ-3 игроков:")
        for i, player in enumerate(report_data['player_stats'][:3], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            attendance_emoji = "🔥" if player['attendance_rate'] >= 80 else "👍" if player['attendance_rate'] >= 60 else "📊"
            print(f"  {medal} {player['player_name']}: {player['attendance_rate']}% {attendance_emoji}")
        
        # Форматируем сообщение
        print("\n📱 Форматирование сообщения для Telegram...")
        message = analytics.format_yearly_report_message(report_data)
        
        print("\n📄 Результат (первые 500 символов):")
        print("-" * 50)
        print(message[:500] + "..." if len(message) > 500 else message)
        print("-" * 50)
        
        print("\n✅ Годовой отчет успешно сгенерирован!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при генерации отчета: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_yearly_report()
    if success:
        print("\n🎉 Тест пройден успешно!")
    else:
        print("\n💥 Тест провален!")
    
    print("\n💡 Примечание: Для отправки отчета в Telegram нужно установить BOT_TOKEN и GROUP_ID")
