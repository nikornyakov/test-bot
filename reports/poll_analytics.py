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
        """Рассчитать статистику игроков за период"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            polls = self.get_polls_by_date_range(cutoff_date.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))
            
            player_stats = {}
            
            for poll_data in polls:
                poll_dict = asdict(poll_data)
                if poll_dict['date'] < cutoff_date.strftime('%Y-%m-%d'):
                    continue
                
                # Анализируем голоса РЕАЛЬНЫХ игроков из списка voters
                voters = poll_dict.get('voters', [])
                votes = poll_dict.get('votes', {})
                
                # Создаем соответствие между вариантами ответов и количеством голосов
                vote_options = []
                for option, count in votes.items():
                    vote_options.extend([option] * count)
                
                # Распределяем голоса между реальными игроками
                for i, voter_id in enumerate(voters):
                    if i < len(vote_options):
                        option = vote_options[i]
                        player_name = self._get_player_name(voter_id, option)
                        
                        if player_name not in player_stats:
                            player_stats[player_name] = {
                                'player_id': voter_id,
                                'player_name': player_name,
                                'total_polls': 0,
                                'attended': 0,
                                'skipped': 0,
                                'maybe': 0,
                                'late': 0
                            }
                        
                        player_stats[player_name]['total_polls'] += 1
                        
                        if 'Буду' in option:
                            player_stats[player_name]['attended'] += 1
                        elif 'Не смогу' in option:
                            player_stats[player_name]['skipped'] += 1
                        elif 'Еще не знаю' in option:
                            player_stats[player_name]['maybe'] += 1
                        elif 'Опоздать' in option:
                            player_stats[player_name]['late'] += 1
            
            # Если нет данных о голосах, используем упрощенный подход
            if not player_stats:
                self.logger.warning("Нет данных о голосах игроков, используем упрощенный подход")
                for poll_data in polls:
                    poll_dict = asdict(poll_data)
                    if poll_dict['date'] < cutoff_date.strftime('%Y-%m-%d'):
                        continue
                        
                    for option, count in poll_dict['votes'].items():
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
            
            # Рассчитываем процент посещаемости и создаем объекты PlayerStats
            result = []
            for player_data in player_stats.values():
                if player_data['total_polls'] > 0:
                    attendance_rate = ((player_data['attended'] + player_data['late']) / 
                                     player_data['total_polls']) * 100
                    
                    result.append(PlayerStats(
                        player_id=player_data['player_id'],
                        player_name=player_data['player_name'],
                        total_polls=player_data['total_polls'],
                        attended=player_data['attended'],
                        skipped=player_data['skipped'],
                        maybe=player_data['maybe'],
                        late=player_data['late'],
                        attendance_rate=round(attendance_rate, 1)
                    ))
            
            return sorted(result, key=lambda x: x.attendance_rate, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Ошибка при расчете статистики игроков: {e}")
            return []
    
    def _get_player_name(self, voter_id: str, fallback_name: str = None) -> str:
        """Получить имя игрока по его ID"""
        try:
            # Здесь можно добавить логику для получения реальных имен
            # из Telegram API или из кэша пользователей
            
            # Проверяем, есть ли у нас информация об этом пользователе
            user_info = self._get_cached_user_info(voter_id)
            if user_info and 'first_name' in user_info:
                name = user_info['first_name']
                if 'last_name' in user_info and user_info['last_name']:
                    name += f" {user_info['last_name']}"
                return name
            
            # Если нет информации, используем ID или fallback
            return fallback_name or f"Player_{voter_id[:8]}"
            
        except Exception:
            return fallback_name or f"Player_{voter_id[:8]}"
    
    def _get_cached_user_info(self, user_id: str) -> dict:
        """Получить кэшированную информацию о пользователе"""
        try:
            # Попытка загрузить из файла с кэшем пользователей
            cache_file = self.data_dir / "user_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    return cache.get(user_id, {})
        except Exception:
            pass
        return {}
    
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
    
    def generate_yearly_report(self, year: int = None) -> Dict[str, Any]:
        """Сгенерировать годовой отчет"""
        try:
            if year is None:
                year = datetime.now().year
                
            start_date = f"{year}-01-01"
            end_date = f"{year+1}-01-01"
            
            polls = self.get_polls_by_date_range(start_date, end_date)
            
            # Если нет опросов за год, пробуем взять данные за последние 365 дней
            if not polls:
                self.logger.warning(f"Нет опросов за {year} год, пробуем взять данные за последние 365 дней")
                player_stats = self.calculate_player_stats(days_back=365)
            else:
                # Для годового отчета берем статистику за весь год
                player_stats = self.calculate_player_stats(days_back=366)
            
            # Общая статистика за год
            total_polls = len(polls)
            total_votes = sum(p.total_votes for p in polls)
            avg_participation = total_votes / total_polls if total_polls > 0 else 0
            
            # Статистика по месяцам
            monthly_stats = {}
            for month in range(1, 13):
                month_start = f"{year}-{month:02d}-01"
                if month == 12:
                    month_end = f"{year+1}-01-01"
                else:
                    month_end = f"{year}-{month+1:02d}-01"
                
                month_polls = self.get_polls_by_date_range(month_start, month_end)
                if month_polls:
                    month_votes = sum(p.total_votes for p in month_polls)
                    monthly_stats[month] = {
                        'month': month,
                        'month_name': self._get_month_name(month),
                        'polls': len(month_polls),
                        'avg_participation': round(month_votes / len(month_polls), 1) if month_polls else 0
                    }
            
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
                'period': f"{year}",
                'total_polls': total_polls,
                'total_votes': total_votes,
                'avg_participation': round(avg_participation, 1),
                'monthly_stats': monthly_stats,
                'attendance_by_date': attendance_by_date,
                'player_stats': [asdict(p) for p in player_stats[:15]]  # Топ-15 игроков за год
            }
        except Exception as e:
            self.logger.error(f"Ошибка при генерации годового отчета: {e}")
            # Возвращаем пустой отчет в случае ошибки
            return {
                'period': f"{year}",
                'total_polls': 0,
                'total_votes': 0,
                'avg_participation': 0,
                'monthly_stats': {},
                'attendance_by_date': {},
                'player_stats': []
            }
    
    def _get_month_name(self, month: int) -> str:
        """Получить название месяца"""
        months = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }
        return months.get(month, '')
    
    def format_yearly_report_message(self, report_data: Dict[str, Any]) -> str:
        """Отформатировать годовой отчет для отправки в Telegram"""
        try:
            period = report_data['period']
            total_polls = report_data['total_polls']
            avg_participation = report_data['avg_participation']
            monthly_stats = report_data['monthly_stats']
            
            # Если нет данных за год
            if total_polls == 0:
                return f"""🏀 *ГОДОВОЙ ОТЧЕТ ПО ПОСЕЩАЕМОСТИ*

📅 *Год:* {period}

🔍 *За {period} год не найдено данных об опросах*

💡 *Возможные причины:*
• Опросы не проводились в этом году
• Нет сохраненных результатов опросов
• Ошибка в сборе данных

📱 *Попробуйте сгенерировать отчет за другой год или проверьте настройки бота*"""
            
            message = f"""🏀 *ГОДОВОЙ ОТЧЕТ ПО ПОСЕЩАЕМОСТИ*

📅 *Год:* {period}

📊 *ОБЩАЯ СТАТИСТИКА ЗА ГОД:*
• Всего тренировок: {total_polls}
• Среднее участие: {avg_participation} человек
• Явка: {round((avg_participation / 8) * 100, 1)}% (из 8 игроков)

📈 *СТАТИСТИКА ПО МЕСЯЦАМ:*

"""
            
            # Добавляем статистику по месяцам
            for month_data in monthly_stats.values():
                month_emoji = "🔥" if month_data['avg_participation'] >= 6 else "👍" if month_data['avg_participation'] >= 4 else "📊"
                message += f"{month_data['month_name']}: {month_data['polls']} тренировок, {month_data['avg_participation']} в среднем {month_emoji}\n"
            
            message += f"""
🏆 *ТОП-10 ИГРОКОВ ЗА ГОД:*

"""
            
            # Добавляем топ игроков за год
            for i, player in enumerate(report_data['player_stats'][:10], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
                attendance_emoji = "🔥" if player['attendance_rate'] >= 80 else "👍" if player['attendance_rate'] >= 60 else "📊"
                
                message += f"{medal} {player['player_name']} {attendance_emoji}\n"
                message += f"   Посещаемость: {player['attendance_rate']}% ({player['attended']}/{player['total_polls']})\n\n"
            
            message += """📈 *АНАЛИТИКА ГОДА:*
• Посещаемость рассчитывается как: (Посетил + Опоздал) / Всего тренировок
• Игроки с посещаемостью ≥80% считаются самыми стабильными
• Месячная статистика показывает динамику посещаемости в течение года

💾 *Полная статистика доступна в файлах проекта*
"""
            
            return message
        except Exception as e:
            self.logger.error(f"Ошибка при форматировании годового отчета: {e}")
            return f"""🏀 *ГОДОВОЙ ОТЧЕТ ПО ПОСЕЩАЕМОСТИ*

❌ *Ошибка при формировании отчета за {report_data.get('period', 'неизвестный год')}*

🔧 *Техническая информация:*
{str(e)}

📱 *Попробуйте запустить отчет еще раз или обратитесь к администратору*"""
    
    def format_report_message(self, report_data: Dict[str, Any]) -> str:
        """Отформатировать отчет для отправки в Telegram"""
        period = report_data['period']
        total_polls = report_data['total_polls']
        avg_participation = report_data['avg_participation']
        
        message = f"""🏀 *ЕЖЕМЕСЯЧНЫЙ ОТЧЕТ ПО ПОСЕЩАЕМОСТИ*

📅 *Период:* {period}

📊 *ОБЩАЯ СТАТИСТИКА:*
• Всего тренировок: {total_polls}
• Среднее участие: {avg_participation} человек
• Явка: {round((avg_participation / 8) * 100, 1)}% (из 8 игроков)

🏆 *ТОП-5 ИГРОКОВ ПО ПОСЕЩАЕМОСТИ:*

"""
        
        # Добавляем топ игроков с более детальной информацией
        for i, player in enumerate(report_data['player_stats'][:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
            attendance_emoji = "🔥" if player['attendance_rate'] >= 80 else "👍" if player['attendance_rate'] >= 60 else "📊"
            
            message += f"{medal} {player['player_name']} {attendance_emoji}\n"
            message += f"   Посещаемость: {player['attendance_rate']}% ({player['attended']}/{player['total_polls']})\n"
            message += f"   Пропустил: {player['skipped']} | Не уверен: {player['maybe']} | Опоздал: {player['late']}\n\n"
        
        message += """📈 *АНАЛИТИКА:*
• Посещаемость рассчитывается как: (Посетил + Опоздал) / Всего тренировок
• Игроки с посещаемостью ≥80% считаются самыми стабильными

💾 *Полная статистика доступна в файлах проекта*
"""
        
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
