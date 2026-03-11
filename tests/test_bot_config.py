import pytest
import json
import tempfile
import os
from bot_config import Config


class TestConfig:
    """Тесты для класса Config"""
    
    def setup_method(self):
        """Создание временного конфигурационного файла для тестов"""
        self.test_config = {
            "schedule": {
                "training_days": [1, 3],
                "poll_days": [0, 2],
                "training_time": "19:00-20:30"
            },
            "venue": {
                "name": "Test Hall",
                "address": "Test Address 123"
            },
            "messages": {
                "welcome": {
                    "title": "Test Welcome",
                    "tuesday": "Tuesday Training"
                },
                "poll": {
                    "options": ["Yes", "No", "Maybe"]
                }
            },
            "team": {
                "name": "Test Team",
                "league": "Test League"
            }
        }
        
        # Создаем временный файл
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_file)
        self.temp_file.close()
        
        self.config = Config(self.temp_file.name)
    
    def teardown_method(self):
        """Удаление временного файла"""
        os.unlink(self.temp_file.name)
    
    def test_load_config_success(self):
        """Тест успешной загрузки конфигурации"""
        assert self.config.get('schedule.training_days') == [1, 3]
        assert self.config.get('venue.name') == "Test Hall"
        assert self.config.get('messages.welcome.title') == "Test Welcome"
    
    def test_get_with_default(self):
        """Тест получения значения с дефолтным значением"""
        assert self.config.get('nonexistent.key', 'default') == 'default'
        assert self.config.get('schedule.nonexistent', 'default') == 'default'
    
    def test_get_schedule(self):
        """Тест получения расписания"""
        schedule = self.config.get_schedule()
        assert schedule['training_days'] == [1, 3]
        assert schedule['poll_days'] == [0, 2]
        assert schedule['training_time'] == "19:00-20:30"
    
    def test_get_venue(self):
        """Тест получения информации о месте"""
        venue = self.config.get_venue()
        assert venue['name'] == "Test Hall"
        assert venue['address'] == "Test Address 123"
    
    def test_get_training_days(self):
        """Тест получения дней тренировок"""
        days = self.config.get_training_days()
        assert days == [1, 3]
    
    def test_get_poll_days(self):
        """Тест получения дней для опросов"""
        days = self.config.get_poll_days()
        assert days == [0, 2]
    
    def test_get_training_time(self):
        """Тест получения времени тренировок"""
        time = self.config.get_training_time()
        assert time == "19:00-20:30"
    
    def test_get_venue_name(self):
        """Тест получения названия зала"""
        name = self.config.get_venue_name()
        assert name == "Test Hall"
    
    def test_get_venue_address(self):
        """Тест получения адреса зала"""
        address = self.config.get_venue_address()
        assert address == "Test Address 123"
    
    def test_get_poll_options(self):
        """Тест получения вариантов опроса"""
        options = self.config.get_poll_options()
        assert options == ["Yes", "No", "Maybe"]
    
    def test_get_poll_question(self):
        """Тест получения вопроса для опроса"""
        question = self.config.get_poll_question(0, "01.01.2024")
        assert "01.01.2024" in question
        
        question = self.config.get_poll_question(2, "02.01.2024")
        assert "02.01.2024" in question
    
    def test_file_not_found(self):
        """Тест обработки отсутствующего файла"""
        with pytest.raises(FileNotFoundError):
            Config("nonexistent_file.json")
    
    def test_invalid_json(self):
        """Тест обработки невалидного JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')
            invalid_file = f.name
        
        try:
            with pytest.raises(ValueError):
                Config(invalid_file)
        finally:
            os.unlink(invalid_file)
    
    def test_default_values(self):
        """Тест значений по умолчанию"""
        # Создаем пустой конфиг
        empty_config = {"schedule": {}, "venue": {}, "messages": {}, "team": {}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(empty_config, f)
            empty_file = f.name
        
        try:
            config = Config(empty_file)
            assert config.get_training_days() == [1, 3]  # дефолтное значение
            assert config.get_poll_days() == [0, 2]  # дефолтное значение
            assert config.get_training_time() == "19:00-20:30"  # дефолтное значение
            assert config.get_venue_name() == "Basket Hall"  # дефолтное значение
            assert config.get_venue_address() == "ул. Салова, 57 корпус 5"  # дефолтное значение
        finally:
            os.unlink(empty_file)
