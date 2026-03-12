"""
Модуль аналитики и отчетов для баскетбольного бота.

Этот модуль предоставляет функциональность для:
- Сбора и хранения результатов опросов
- Анализа посещаемости тренировок
- Генерации отчетов
- Отправки статистики в Telegram
"""

from .poll_analytics import PollAnalytics, PollResult, PlayerStats
from .poll_tracker import PollTracker
from .generate_reports import (
    generate_monthly_report,
    generate_attendance_report, 
    generate_full_report,
    generate_test_data
)

__all__ = [
    'PollAnalytics',
    'PollResult', 
    'PlayerStats',
    'PollTracker',
    'generate_monthly_report',
    'generate_attendance_report',
    'generate_full_report',
    'generate_test_data'
]

__version__ = '1.0.0'
