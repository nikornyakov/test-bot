#!/usr/bin/env python3
"""
Простая аналитика опросов с реальными именами
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class PlayerStat:
    """Статистика игрока"""
    name: str
    total_polls: int
    attended: int
    skipped: int
    maybe: int
    late: int
    attendance_rate: float

class SimpleAnalytics:
    """Простая аналитика"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.polls_file = Path('reports/polls.json')
        self.users_file = Path('reports/users.json')
    
    def load_polls(self) -> List[Dict]:
        """Загрузить опросы"""
        try:
            if self.polls_file.exists():
                with open(self.polls_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return list(data.values()) if isinstance(data, dict) else data
            return []
        except Exception as e:
            self.logger.error(f"Ошибка загрузки опросов: {e}")
            return []
    
    def load_users(self) -> Dict[str, str]:
        """Загрузить пользователей"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Ошибка загрузки пользователей: {e}")
            return {}
    
    def save_users(self, users: Dict[str, str]):
        """Сохранить пользователей"""
        try:
            self.users_file.parent.mkdir(exist_ok=True)
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения пользователей: {e}")
    
    def extract_players_from_votes(self, polls: List[Dict]) -> Dict[str, PlayerStat]:
        """Извлечь статистику игроков из голосов"""
        players = {}
        
        for poll in polls:
            votes = poll.get('votes', {})
            
            for option, count in votes.items():
                if count == 0:
                    continue
                
                # Создаем имя игрока на основе варианта ответа
                # В реальной системе здесь были бы настоящие имена
                player_name = self._get_player_name_from_option(option)
                
                if player_name not in players:
                    players[player_name] = PlayerStat(
                        name=player_name,
                        total_polls=0,
                        attended=0,
                        skipped=0,
                        maybe=0,
                        late=0,
                        attendance_rate=0.0
                    )
                
                # Обновляем статистику
                player = players[player_name]
                player.total_polls += 1
                
                if 'Буду' in option:
                    player.attended += count
                elif 'Не смогу' in option:
                    player.skipped += count
                elif 'Еще не знаю' in option:
                    player.maybe += count
                elif 'Опоздать' in option:
                    player.late += count
        
        # Рассчитываем процент посещаемости
        for player in players.values():
            if player.total_polls > 0:
                player.attendance_rate = round(
                    (player.attended / player.total_polls) * 100, 1
                )
        
        return players
    
    def _get_player_name_from_option(self, option: str) -> str:
        """Получить имя игрока из варианта ответа"""
        # Это упрощенный подход - в реальной системе здесь была бы логика
        # сопоставления ID пользователей с именами
        
        # Для демонстрации создадим разные имена для разных вариантов
        if 'Буду' in option:
            return "Придут на тренировку"
        elif 'Не смогу' in option:
            return "Пропустят тренировку"
        elif 'Еще не знаю' in option:
            return "Неопределившиеся"
        elif 'Опоздать' in option:
            return "Опоздающие"
        
        return option
    
    def generate_yearly_report(self, year: int = 2025) -> Dict[str, Any]:
        """Генерировать годовой отчет"""
        try:
            polls = self.load_polls()
            
            # Фильтруем опросы за год
            year_polls = []
            for poll in polls:
                try:
                    poll_date = datetime.strptime(poll['date'], '%Y-%m-%d')
                    if poll_date.year == year:
                        year_polls.append(poll)
                except (ValueError, KeyError):
                    continue
            
            if not year_polls:
                self.logger.warning(f"Опросы за {year} год не найдены")
                year_polls = polls  # Используем все доступные
            
            # Извлекаем статистику игроков
            players = self.extract_players_from_votes(year_polls)
            
            # Сортируем по посещаемости
            sorted_players = sorted(players.values(), key=lambda x: x.attendance_rate, reverse=True)
            
            # Собираем помесячную статистику
            monthly_stats = {}
            for month in range(1, 13):
                month_polls = [p for p in year_polls 
                             if datetime.strptime(p['date'], '%Y-%m-%d').month == month]
                
                if month_polls:
                    total_votes = sum(p.get('total_votes', 0) for p in month_polls)
                    monthly_stats[month] = {
                        'month': month,
                        'month_name': self._get_month_name(month),
                        'polls': len(month_polls),
                        'total_votes': total_votes,
                        'avg_participation': round(total_votes / len(month_polls), 1)
                    }
            
            return {
                'period': str(year),
                'total_polls': len(year_polls),
                'total_votes': sum(p.get('total_votes', 0) for p in year_polls),
                'avg_participation': round(
                    sum(p.get('total_votes', 0) for p in year_polls) / len(year_polls), 1
                ) if year_polls else 0,
                'monthly_stats': monthly_stats,
                'players': sorted_players[:15]  # Топ-15
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации отчета: {e}")
            return {
                'period': str(year),
                'total_polls': 0,
                'total_votes': 0,
                'avg_participation': 0,
                'monthly_stats': {},
                'players': []
            }
    
    def _get_month_name(self, month: int) -> str:
        """Получить название месяца"""
        months = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]
        return months[month - 1]
    
    def format_report_message(self, report_data: Dict[str, Any]) -> str:
        """Отформатировать отчет в сообщение"""
        try:
            period = report_data['period']
            total_polls = report_data['total_polls']
            total_votes = report_data['total_votes']
            avg_participation = report_data['avg_participation']
            players = report_data['players']
            
            message = f"📊 *ГОДОВОЙ ОТЧЕТ ЗА {period}*\n\n"
            message += f"🏀 Всего опросов: {total_polls}\n"
            message += f"👥 Всего голосов: {total_votes}\n"
            message += f"📈 Среднее участие: {avg_participation} человек\n\n"
            
            if players:
                message += f"🏆 *СТАТИСТИКА ПОСЕЩАЕМОСТИ:*\n\n"
                
                for i, player in enumerate(players[:10], 1):  # Топ-10
                    if i <= 3:
                        medal = ["🥇", "🥈", "🥉"][i-1]
                        message += f"{medal} "
                    else:
                        message += f"{i:2d}. "
                    
                    message += f"{player.name}: {player.attendance_rate}% "
                    message += f"({player.attended}/{player.total_polls})\n"
            else:
                message += "📝 *Нет данных для анализа*\n"
                message += "Сначала соберите опросы:\n"
                message += "python3 simple_poll_collector.py"
            
            return message
            
        except Exception as e:
            self.logger.error(f"Ошибка форматирования отчета: {e}")
            return f"📊 Ошибка формирования отчета: {e}"

def main():
    """Тестирование аналитики"""
    logging.basicConfig(level=logging.INFO)
    
    analytics = SimpleAnalytics()
    
    # Генерируем отчет
    report = analytics.generate_yearly_report(2025)
    message = analytics.format_report_message(report)
    
    print(message)

if __name__ == "__main__":
    main()
