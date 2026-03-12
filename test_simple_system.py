#!/usr/bin/env python3
"""
Тестирование простой системы сбора данных
"""

import json
import os
from pathlib import Path
from datetime import datetime

def create_demo_polls():
    """Создать демо-данные опросов"""
    
    # Демо опросы
    demo_polls = {
        "poll_001_20250301": {
            "poll_id": "poll_001_20250301",
            "date": "2025-03-01",
            "question": "Тренировка 01.03.2025 в 19:00",
            "training_date": "01.03.2025",
            "total_votes": 12,
            "options": ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Планирую опоздать"],
            "votes": {
                "✅ Буду": 8,
                "❌ Не смогу": 2,
                "🤔 Еще не знаю": 1,
                "⏰ Планирую опоздать": 1
            },
            "message_id": 123,
            "created_at": "2025-03-01T10:00:00"
        },
        "poll_002_20250305": {
            "poll_id": "poll_002_20250305",
            "date": "2025-03-05",
            "question": "Тренировка 05.03.2025 в 19:00",
            "training_date": "05.03.2025",
            "total_votes": 14,
            "options": ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Планирую опоздать"],
            "votes": {
                "✅ Буду": 10,
                "❌ Не смогу": 2,
                "🤔 Еще не знаю": 1,
                "⏰ Планирую опоздать": 1
            },
            "message_id": 124,
            "created_at": "2025-03-05T10:00:00"
        },
        "poll_003_20250308": {
            "poll_id": "poll_003_20250308",
            "date": "2025-03-08",
            "question": "Тренировка 08.03.2025 в 19:00",
            "training_date": "08.03.2025",
            "total_votes": 13,
            "options": ["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Планирую опоздать"],
            "votes": {
                "✅ Буду": 9,
                "❌ Не смогу": 2,
                "🤔 Еще не знаю": 1,
                "⏰ Планирую опоздать": 1
            },
            "message_id": 125,
            "created_at": "2025-03-08T10:00:00"
        }
    }
    
    # Сохраняем файл
    Path('reports').mkdir(exist_ok=True)
    with open('reports/polls.json', 'w', encoding='utf-8') as f:
        json.dump(demo_polls, f, ensure_ascii=False, indent=2)
    
    print("✅ Демо-данные опросов созданы")
    print(f"📊 Всего опросов: {len(demo_polls)}")
    print(f"📁 Файл: reports/polls.json")

def test_simple_analytics():
    """Тестировать простую аналитику"""
    try:
        from simple_analytics import SimpleAnalytics
        
        print("\n📈 Тестирование аналитики...")
        analytics = SimpleAnalytics()
        
        # Генерируем отчет
        report = analytics.generate_yearly_report(2025)
        message = analytics.format_report_message(report)
        
        print("\n📊 ОТЧЕТ:")
        print("=" * 40)
        print(message)
        print("=" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка аналитики: {e}")
        return False

def test_data_collection():
    """Тестировать сбор данных (демо)"""
    print("\n🔍 Тестирование сбора данных...")
    
    # Проверяем наличие данных
    polls_file = Path('reports/polls.json')
    if polls_file.exists():
        with open(polls_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📋 Найдено опросов: {len(data)}")
        
        # Показываем последние опросы
        for poll_id, poll_data in list(data.items())[-2:]:
            print(f"• {poll_data['question']} ({poll_data['date']})")
            print(f"  Голосов: {poll_data['total_votes']}")
        
        return True
    else:
        print("❌ Файл polls.json не найден")
        return False

def main():
    """Основная функция"""
    print("🧪 ТЕСТИРОВАНИЕ ПРОСТОЙ СИСТЕМЫ")
    print("=" * 50)
    
    # 1. Создаем демо-данные
    create_demo_polls()
    
    # 2. Тестируем сбор данных
    collection_ok = test_data_collection()
    
    # 3. Тестируем аналитику
    analytics_ok = test_simple_analytics()
    
    # 4. Итоги
    print("\n🎉 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"📊 Сбор данных: {'✅' if collection_ok else '❌'}")
    print(f"📈 Аналитика: {'✅' if analytics_ok else '❌'}")
    
    if collection_ok and analytics_ok:
        print("\n🚀 Система готова к работе!")
        print("\n📋 ДАЛЬНЕЙШИЕ ШАГИ:")
        print("1. Установите реальный BOT_TOKEN в .env")
        print("2. Получите реальный GROUP_ID")
        print("3. Запустите сбор данных: python3 simple_poll_collector.py")
        print("4. Генерируйте отчеты: python3 reports/generate_reports.py yearly 2025")
    else:
        print("\n💥 Есть проблемы, нужно исправить")

if __name__ == "__main__":
    main()
