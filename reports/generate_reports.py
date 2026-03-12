import asyncio
import sys
import logging
from datetime import datetime, timedelta
import os

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Для импорта при запуске как модуля
try:
    from .poll_tracker import PollTracker
    from .poll_analytics import PollAnalytics, create_mock_poll_result
except ImportError:
    # Для импорта при запуске как скрипта
    from poll_tracker import PollTracker
    from poll_analytics import PollAnalytics, create_mock_poll_result


async def generate_monthly_report(year: int = None, month: int = None):
    """Генерация и отправка месячного отчета"""
    tracker = PollTracker()
    
    if not await tracker.initialize_bot():
        print("Ошибка инициализации бота")
        return False
    
    success = await tracker.send_monthly_report(year, month)
    return success


async def generate_attendance_report(days: int = 30):
    """Генерация и отправка отчета по посещаемости"""
    tracker = PollTracker()
    
    if not await tracker.initialize_bot():
        print("Ошибка инициализации бота")
        return False
    
    success = await tracker.send_attendance_stats(days)
    return success


async def generate_full_report():
    """Генерация полного отчета (месячный + посещаемость)"""
    tracker = PollTracker()
    
    if not await tracker.initialize_bot():
        print("Ошибка инициализации бота")
        return False
    
    # Отправляем месячный отчет
    month_success = await tracker.send_monthly_report()
    
    # Ждем немного между сообщениями
    await asyncio.sleep(2)
    
    # Отправляем статистику посещаемости
    attendance_success = await tracker.send_attendance_stats(30)
    
    return month_success and attendance_success


async def generate_test_data():
    """Создать тестовые данные для демонстрации"""
    analytics = PollAnalytics()
    
    # Создаем несколько тестовых опросов за последние дни
    base_date = datetime.now() - timedelta(days=10)
    
    for i in range(5):
        # Создаем тестовый результат
        mock_result = create_mock_poll_result()
        
        # Изменяем дату
        test_date = base_date + timedelta(days=i*2)
        mock_result.date = test_date.strftime('%Y-%m-%d')
        mock_result.training_date = test_date.strftime('%d.%m.%Y')
        mock_result.poll_id = f"test_poll_{i}_{test_date.strftime('%Y%m%d')}"
        
        # Варьируем количество голосов
        mock_result.total_votes = 6 + i
        mock_result.votes = {
            "✅ Буду": 3 + i,
            "❌ Не смогу": 1,
            "🤔 Еще не знаю": 1,
            "⏰ Планирую опоздать": 1 if i > 2 else 0
        }
        
        # Сохраняем
        analytics.save_poll_result(mock_result)
        print(f"Создан тестовый опрос от {mock_result.date}")
    
    print("Тестовые данные созданы успешно!")


async def main():
    """Основная функция"""
    logger = logging.getLogger(__name__)
    logger.info("Запуск генератора отчетов")
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python generate_reports.py monthly [год] [месяц]")
        print("  python generate_reports.py attendance [дни]")
        print("  python generate_reports.py full")
        print("  python generate_reports.py test_data")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "monthly":
            year = int(sys.argv[2]) if len(sys.argv) > 2 else None
            month = int(sys.argv[3]) if len(sys.argv) > 3 else None
            success = await generate_monthly_report(year, month)
            print(f"Месячный отчет {'отправлен' if success else 'не отправлен'}")
        
        elif command == "attendance":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            success = await generate_attendance_report(days)
            print(f"Отчет по посещаемости за {days} дней {'отправлен' if success else 'не отправлен'}")
        
        elif command == "full":
            success = await generate_full_report()
            print(f"Полный отчет {'отправлен' if success else 'не отправлен'}")
        
        elif command == "test_data":
            await generate_test_data()
        
        else:
            print(f"Неизвестная команда: {command}")
    
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды {command}: {e}")
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
