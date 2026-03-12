import asyncio
import sys
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем простую аналитику
try:
    from .simple_analytics import SimpleAnalytics
except ImportError:
    from simple_analytics import SimpleAnalytics

# Импортируем базовый класс бота
try:
    from .bot_base import TelegramBotBase
except ImportError:
    from bot_base import TelegramBotBase


async def generate_monthly_report(year: int = None, month: int = None):
    """Генерация и отправка месячного отчета"""
    analytics = SimpleAnalytics()
    bot = TelegramBotBase()
    
    if not await bot.initialize_bot():
        print("Ошибка инициализации бота")
        return False
    
    # Генерируем отчет
    report_data = analytics.generate_yearly_report(year)
    message = analytics.format_report_message(report_data)
    
    # Отправляем сообщение
    success = await bot.send_message(message, parse_mode='Markdown')
    
    if success:
        print(f"Месячный отчет за {year or datetime.now().year}-{month or datetime.now().month} отправлен")
    else:
        print("Ошибка отправки отчета")
    
    return success


async def generate_attendance_report(days: int = 30):
    """Генерация и отправка отчета по посещаемости"""
    analytics = SimpleAnalytics()
    bot = TelegramBotBase()
    
    if not await bot.initialize_bot():
        print("Ошибка инициализации бота")
        return False
    
    # Генерируем отчет
    report_data = analytics.generate_yearly_report(datetime.now().year)
    message = analytics.format_report_message(report_data)
    
    # Отправляем сообщение
    success = await bot.send_message(message, parse_mode='Markdown')
    
    if success:
        print(f"Отчет по посещаемости за последние {days} дней отправлен")
    else:
        print("Ошибка отправки отчета")
    
    return success


async def generate_yearly_report(year: int = None):
    """Генерация и отправка годового отчета с простой аналитикой"""
    try:
        # Используем простую аналитику
        analytics = SimpleAnalytics()
        bot = TelegramBotBase()
        
        if not await bot.initialize_bot():
            print("Ошибка инициализации бота")
            return False
        
        # Генерируем отчет
        report_data = analytics.generate_yearly_report(year)
        message = analytics.format_report_message(report_data)
        
        # Отправляем сообщение
        success = await bot.send_message(message, parse_mode='Markdown')
        
        if success:
            print(f"Годовой отчет за {year or datetime.now().year} отправлен")
        else:
            print("Ошибка отправки отчета")
        
        return success
        
    except Exception as e:
        print(f"Ошибка при генерации годового отчета: {e}")
        return False


async def generate_full_report():
    """Генерация полного отчета"""
    analytics = SimpleAnalytics()
    bot = TelegramBotBase()
    
    if not await bot.initialize_bot():
        print("Ошибка инициализации бота")
        return False
    
    # Генерируем отчет
    report_data = analytics.generate_yearly_report(datetime.now().year)
    message = analytics.format_report_message(report_data)
    
    # Отправляем сообщение
    success = await bot.send_message(message, parse_mode='Markdown')
    
    if success:
        print("Полный отчет отправлен")
    else:
        print("Ошибка отправки отчета")
    
    return success


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
        print("  python generate_reports.py yearly [год]")
        print("  python generate_reports.py full")
        print("  python generate_reports.py test_data")
        return
    
    command = sys.argv[1].lower()
    
    if command == "monthly":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else None
        month = int(sys.argv[3]) if len(sys.argv) > 3 else None
        success = await generate_monthly_report(year, month)
    elif command == "attendance":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        success = await generate_attendance_report(days)
    elif command == "yearly":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else None
        success = await generate_yearly_report(year)
    elif command == "full":
        success = await generate_full_report()
    else:
        print(f"Неизвестная команда: {command}")
        success = False
    
    if success:
        print("✅ Отчет успешно отправлен")
    else:
        print("❌ Ошибка при отправке отчета")


if __name__ == "__main__":
    asyncio.run(main())
