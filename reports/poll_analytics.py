import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class PollResult:
    """Результат опроса"""
    poll_id: str
    date: str
    question: str
    training_date: str
    total_votes: int
    options: List[str]
    votes: Dict[str, int]
    voters: List[str]
    created_at: str


@dataclass
class PlayerStats:
    """Статистика игрока"""
    player_id: str
    player_name: str
    total_polls: int
    attended: int
    skipped: int
    maybe: int
    late: int
    attendance_rate: float


class PollAnalytics:
    """Класс для аналитики опросов"""
    
    def __init__(self, data_dir: str = "reports"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.polls_file = self.data_dir / "polls.json"
        self.stats_file = self.data_dir / "stats.json"
        self.logger = logging.getLogger(__name__)
        
    def save_poll_result(self, poll_result: PollResult) -> bool:
        """Сохранить результат опроса"""
        try:
            # Загружаем существующие результаты
            polls = self.load_all_polls()
            
            # Добавляем новый результат
            polls[poll_result.poll_id] = asdict(poll_result)
            
            # Сохраняем в файл
            with open(self.polls_file, 'w', encoding='utf-8') as f:
                json.dump(polls, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Результат опроса {poll_result.poll_id} сохранен")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения результата опроса: {e}")
            return False
    
    def load_all_polls(self) -> Dict[str, Dict]:
        """Загрузить все результаты опросов"""
        try:
            if self.polls_file.exists():
                with open(self.polls_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Ошибка загрузки результатов опросов: {e}")
            return {}
    
    def get_polls_by_date_range(self, start_date: str, end_date: str) -> List[PollResult]:
        """Получить опросы за период"""
        polls = self.load_all_polls()
        result = []
        
        for poll_data in polls.values():
            poll_date = datetime.strptime(poll_data['date'], '%Y-%m-%d').date()
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start <= poll_date <= end:
                result.append(PollResult(**poll_data))
        
        return sorted(result, key=lambda x: x.date)
    
    def calculate_player_stats(self, days_back: int = 30) -> List[PlayerStats]:
        """Рассчитать статистику игроков"""
        polls = self.load_all_polls()
        player_stats = {}
        
        # Фильтруем опросы за последние дни
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        for poll_data in polls.values():
            if poll_data['date'] < cutoff_date:
                continue
                
            # Анализируем голоса
            for option, count in poll_data['votes'].items():
                # Это упрощенный подход - в реальности нужно получать ID игроков
                # Для демонстрации используем опции как идентификаторы
                player_id = option
                if player_id not in player_stats:
                    player_stats[player_id] = {
                        'player_id': player_id,
                        'player_name': option,
                        'total_polls': 0,
                        'attended': 0,
                        'skipped': 0,
                        'maybe': 0,
                        'late': 0
                    }
                
                player_stats[player_id]['total_polls'] += 1
                
                if 'Буду' in option:
                    player_stats[player_id]['attended'] += count
                elif 'Не смогу' in option:
                    player_stats[player_id]['skipped'] += count
                elif 'Еще не знаю' in option:
                    player_stats[player_id]['maybe'] += count
                elif 'Опоздать' in option:
                    player_stats[player_id]['late'] += count
        
        # Рассчитываем процент посещаемости
        result = []
        for stats in player_stats.values():
            total = stats['total_polls']
            if total > 0:
                attendance_rate = (stats['attended'] + stats['late']) / total * 100
            else:
                attendance_rate = 0
                
            result.append(PlayerStats(
                player_id=stats['player_id'],
                player_name=stats['player_name'],
                total_polls=stats['total_polls'],
                attended=stats['attended'],
                skipped=stats['skipped'],
                maybe=stats['maybe'],
                late=stats['late'],
                attendance_rate=round(attendance_rate, 1)
            ))
        
        return sorted(result, key=lambda x: x.attendance_rate, reverse=True)
    
    def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """Сгенерировать месячный отчет"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        polls = self.get_polls_by_date_range(start_date, end_date)
        player_stats = self.calculate_player_stats(days_back=60)
        
        # Общая статистика
        total_polls = len(polls)
        total_votes = sum(p.total_votes for p in polls)
        avg_participation = total_votes / total_polls if total_polls > 0 else 0
        
        # Посещаемость по тренировкам
        attendance_by_date = {}
        for poll in polls:
            attendance_by_date[poll.date] = {
                'date': poll.date,
                'training_date': poll.training_date,
                'total_votes': poll.total_votes,
                'attended': poll.votes.get('✅ Буду', 0),
                'skipped': poll.votes.get('❌ Не смогу', 0),
                'maybe': poll.votes.get('🤔 Еще не знаю', 0),
                'late': poll.votes.get('⏰ Планирую опоздать', 0)
            }
        
        return {
            'period': f"{year}-{month:02d}",
            'total_polls': total_polls,
            'total_votes': total_votes,
            'avg_participation': round(avg_participation, 1),
            'attendance_by_date': attendance_by_date,
            'player_stats': [asdict(p) for p in player_stats[:10]]  # Топ-10 игроков
        }
    
    def format_report_message(self, report_data: Dict[str, Any]) -> str:
        """Отформатировать отчет для отправки в Telegram"""
        period = report_data['period']
        total_polls = report_data['total_polls']
        avg_participation = report_data['avg_participation']
        
        message = f"""📊 *ОТЧЕТ ПО ПОСЕЩАЕМОСТИ ЗА {period}*

🏀 *Общая статистика:*
• Всего тренировок: {total_polls}
• Среднее участие: {avg_participation} человек
• Топ-10 игроков по посещаемости:

"""
        
        # Добавляем топ игроков
        for i, player in enumerate(report_data['player_stats'][:5], 1):
            message += f"{i}. {player['player_name']}: {player['attendance_rate']}% ({player['attended']}/{player['total_polls']})\n"
        
        message += "\n📈 *Детальная статистика доступна в файлах проекта*"
        
        return message


def create_mock_poll_result() -> PollResult:
    """Создать тестовый результат опроса"""
    return PollResult(
        poll_id=f"poll_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        date=datetime.now().strftime('%Y-%m-%d'),
        question="Баскетбол во вторник (12.03.2024) 🏀",
        training_date="12.03.2024",
        total_votes=8,
        options=["✅ Буду", "❌ Не смогу", "🤔 Еще не знаю", "⏰ Планирую опоздать"],
        votes={"✅ Буду": 5, "❌ Не смогу": 1, "🤔 Еще не знаю": 1, "⏰ Планирую опоздать": 1},
        voters=["user1", "user2", "user3", "user4", "user5", "user6", "user7", "user8"],
        created_at=datetime.now().isoformat()
    )
